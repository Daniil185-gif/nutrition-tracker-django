from __future__ import annotations

from datetime import date as date_type
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.dateparse import parse_date
from django.utils.timezone import localdate

from .forms import FoodEntryForm, ProductForm
from .models import FoodEntry, Product
from users.models import CustomUser


CALORIES_PER_PROTEIN_GRAM = Decimal('4')
CALORIES_PER_FAT_GRAM = Decimal('9')
CALORIES_PER_CARB_GRAM = Decimal('4')


@login_required
def product_list_view(request):
    q = (request.GET.get('q') or '').strip()
    products = Product.objects.all()
    if q:
        products = products.filter(name__icontains=q)

    return render(
        request,
        'diary/product_list.html',
        {
            'products': products,
            'q': q,
        },
    )


@login_required
def add_product_view(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save(created_by=request.user)
            messages.success(request, 'Продукт добавлен.')
            return redirect('product_list')
    else:
        form = ProductForm()

    return render(request, 'diary/add_product.html', {'form': form})


def _get_selected_date(request, date_str: str | None) -> date_type:
    if date_str:
        parsed = parse_date(date_str)
        if parsed:
            return parsed
    parsed = parse_date(request.GET.get('date') or '')
    return parsed or localdate()


def _calculate_nutrition_norms(user):
    profile = getattr(user, 'profile', None)
    calories = Decimal(getattr(profile, 'daily_calorie_goal', 2000) or 2000)
    weight = getattr(profile, 'weight_kg', None)

    if weight:
        protein = Decimal(weight) * Decimal('1.60')
        fats = Decimal(weight) * Decimal('0.80')
        used_calories = (
            protein * CALORIES_PER_PROTEIN_GRAM
            + fats * CALORIES_PER_FAT_GRAM
        )
        carbs = max(
            Decimal('0'),
            (calories - used_calories) / CALORIES_PER_CARB_GRAM,
        )
    else:
        protein = calories * Decimal('0.20') / CALORIES_PER_PROTEIN_GRAM
        fats = calories * Decimal('0.30') / CALORIES_PER_FAT_GRAM
        carbs = calories * Decimal('0.50') / CALORIES_PER_CARB_GRAM

    return {
        'calories': calories,
        'proteins': protein,
        'fats': fats,
        'carbs': carbs,
    }


def _build_diary_context(owner, selected_date, *, viewer):
    entries = list(
        FoodEntry.objects.select_related('product')
        .filter(user=owner, date=selected_date)
        .order_by('meal', 'created_at')
    )

    recipe_ids = [e.recipe_object_id for e in entries if not e.product_id and e.recipe_object_id]
    recipes_by_id = {}
    if recipe_ids:
        from recipes.models import Recipe  # noqa: PLC0415

        recipes_by_id = {
            r.id: r
            for r in Recipe.objects.filter(id__in=recipe_ids)
        }

    totals = {
        'calories': Decimal('0'),
        'proteins': Decimal('0'),
        'fats': Decimal('0'),
        'carbs': Decimal('0'),
    }

    for entry in entries:
        if entry.product_id:
            ratio = Decimal(entry.grams) / Decimal('100')
            entry.calories = Decimal(entry.product.calories_per_100g) * ratio
            entry.proteins = entry.product.proteins * ratio
            entry.fats = entry.product.fats * ratio
            entry.carbs = entry.product.carbs * ratio
        else:
            recipe = recipes_by_id.get(entry.recipe_object_id)
            entry.recipe_title = getattr(recipe, 'title', '—')
            servings = Decimal(entry.servings or 0)
            if recipe is not None:
                entry.calories = Decimal(recipe.total_calories()) * servings
                entry.proteins = Decimal(recipe.total_proteins()) * servings
                entry.fats = Decimal(recipe.total_fats()) * servings
                entry.carbs = Decimal(recipe.total_carbs()) * servings
            else:
                entry.calories = Decimal('0')
                entry.proteins = Decimal('0')
                entry.fats = Decimal('0')
                entry.carbs = Decimal('0')

        totals['calories'] += entry.calories
        totals['proteins'] += entry.proteins
        totals['fats'] += entry.fats
        totals['carbs'] += entry.carbs

    norms = _calculate_nutrition_norms(owner)
    remaining = {
        key: norms[key] - totals[key]
        for key in norms
    }

    return {
        'selected_date': selected_date,
        'entries': entries,
        'totals': totals,
        'norms': norms,
        'remaining': remaining,
        'diary_owner': owner,
        'is_own_diary': owner == viewer,
    }


@login_required
def diary_view(request, date_str: str | None = None):
    selected_date = _get_selected_date(request, date_str)

    return render(
        request,
        'diary/diary.html',
        _build_diary_context(request.user, selected_date, viewer=request.user),
    )


@login_required
def friend_diary_view(request, username, date_str: str | None = None):
    diary_owner = CustomUser.objects.filter(username=username).select_related('profile').first()
    if diary_owner is None:
        return redirect('find_friends')
    if diary_owner == request.user:
        return redirect('diary')

    is_friend = request.user.friends.filter(pk=diary_owner.pk).exists()
    can_view_diary = diary_owner.profile.show_diary_to_friends and is_friend
    if not can_view_diary:
        return HttpResponseForbidden('Дневник пользователя недоступен.')

    selected_date = _get_selected_date(request, date_str)
    return render(
        request,
        'diary/diary.html',
        _build_diary_context(diary_owner, selected_date, viewer=request.user),
    )


@login_required
def add_food_entry_view(request):
    if request.method == 'POST':
        form = FoodEntryForm(request.POST, user=request.user)
        if form.is_valid():
            entry = form.save(user=request.user)
            messages.success(request, 'Запись добавлена.')
            return redirect(f"{reverse('diary')}?date={entry.date.isoformat()}")
    else:
        initial_date = parse_date(request.GET.get('date') or '') or localdate()
        initial = {'date': initial_date}
        recipe_id = (request.GET.get('recipe') or '').strip()
        if recipe_id.isdigit():
            from recipes.models import Recipe  # noqa: PLC0415

            recipe = Recipe.objects.filter(pk=int(recipe_id)).first()
            if recipe is not None:
                initial['servings'] = '1.00'
                form = FoodEntryForm(initial=initial, user=request.user)
                form.fields['recipe'].initial = recipe
            else:
                form = FoodEntryForm(initial=initial, user=request.user)
        else:
            form = FoodEntryForm(initial=initial, user=request.user)

    return render(request, 'diary/add_food_entry.html', {'form': form})
