from __future__ import annotations

from datetime import date as date_type

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.dateparse import parse_date
from django.utils.timezone import localdate

from .forms import FoodEntryForm, ProductForm
from .models import FoodEntry, Product


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


@login_required
def diary_view(request, date_str: str | None = None):
    selected_date = _get_selected_date(request, date_str)
    entries = (
        FoodEntry.objects.select_related('product')
        .filter(user=request.user, date=selected_date)
        .order_by('meal', 'created_at')
    )

    total_calories = 0
    for entry in entries:
        entry.calories = (entry.grams * entry.product.calories_per_100g) / 100
        total_calories += entry.calories

    return render(
        request,
        'diary/diary.html',
        {
            'selected_date': selected_date,
            'entries': entries,
            'total_calories': total_calories,
        },
    )


@login_required
def add_food_entry_view(request):
    if request.method == 'POST':
        form = FoodEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(user=request.user)
            messages.success(request, 'Запись добавлена.')
            return redirect(f"{reverse('diary')}?date={entry.date.isoformat()}")
    else:
        initial_date = parse_date(request.GET.get('date') or '') or localdate()
        form = FoodEntryForm(initial={'date': initial_date})

    return render(request, 'diary/add_food_entry.html', {'form': form})
