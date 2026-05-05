from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from diary.models import Product

from .forms import RecipeForm, RecipeIngredientForm
from .models import Recipe, RecipeIngredient


def _available_recipes_queryset(user):
    return Recipe.objects.select_related('author').prefetch_related('ingredients').filter(
        Q(author=user) | Q(author__in=user.friends.all()),
    ).distinct()


def _can_view_recipe(user, recipe):
    return recipe.author_id == user.id or user.friends.filter(pk=recipe.author_id).exists()


def _serialize_recipe(recipe: Recipe):
    return {
        'id': recipe.id,
        'title': recipe.title,
        'description': recipe.description,
        'author': recipe.author.username,
        'servings': recipe.servings,
        'cook_time_minutes': recipe.cook_time_minutes,
        'total_calories': float(recipe.total_calories()),
        'total_proteins': float(recipe.total_proteins()),
        'total_fats': float(recipe.total_fats()),
        'total_carbs': float(recipe.total_carbs()),
        'ingredients': [
            {
                'name': ingredient.name,
                'grams': float(ingredient.grams),
                'calories': float(ingredient.calories()),
                'proteins': float(ingredient.proteins()),
                'fats': float(ingredient.fats()),
                'carbs': float(ingredient.carbs()),
            }
            for ingredient in recipe.ingredients.all()
        ],
    }

def _api_ensure_auth(request):
    if not getattr(request, 'user', None) or not request.user.is_authenticated:
        return JsonResponse({'detail': 'Authentication credentials were not provided.'}, status=401)
    return None


@login_required
def recipe_list_view(request):
    recipes = _available_recipes_queryset(request.user)
    return render(request, 'recipes/recipe_list.html', {'recipes': recipes})


@login_required
def recipe_detail_view(request, recipe_id):
    recipe = get_object_or_404(Recipe.objects.select_related('author').prefetch_related('ingredients'), pk=recipe_id)
    if not _can_view_recipe(request.user, recipe):
        return redirect('recipe_list')

    return render(request, 'recipes/recipe_detail.html', {'recipe': recipe})


@login_required
def add_recipe_view(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()
            return redirect('recipe_detail', recipe_id=recipe.id)
    else:
        form = RecipeForm()

    return render(
        request,
        'recipes/add_recipe.html',
        {
            'form': form,
            'page_title': 'Добавить рецепт',
            'submit_label': 'Сохранить',
        },
    )


@login_required
def edit_recipe_view(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id, author=request.user)

    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        if form.is_valid():
            form.save()
            return redirect('recipe_detail', recipe_id=recipe.id)
    else:
        form = RecipeForm(instance=recipe)

    return render(
        request,
        'recipes/add_recipe.html',
        {
            'form': form,
            'recipe': recipe,
            'page_title': 'Редактировать рецепт',
            'submit_label': 'Сохранить изменения',
        },
    )


@login_required
def delete_recipe_view(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id, author=request.user)

    if request.method == 'POST':
        recipe.delete()
        return redirect('recipe_list')

    return render(request, 'recipes/delete_recipe.html', {'recipe': recipe})


@login_required
def add_recipe_ingredient_view(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id, author=request.user)

    if request.method == 'POST':
        form = RecipeIngredientForm(request.POST)
        if form.is_valid():
            ingredient = form.save(commit=False)
            ingredient.recipe = recipe
            ingredient.save()
            return redirect('recipe_detail', recipe_id=recipe.id)
    else:
        form = RecipeIngredientForm()

    context = {
        'form': form,
        'recipe': recipe,
        'page_title': 'Добавить ингредиент',
        'submit_label': 'Сохранить',
    }
    return render(request, 'recipes/add_ingredient.html', context)


@login_required
def edit_recipe_ingredient_view(request, ingredient_id):
    ingredient = get_object_or_404(
        RecipeIngredient.objects.select_related('recipe'),
        pk=ingredient_id,
        recipe__author=request.user,
    )

    if request.method == 'POST':
        form = RecipeIngredientForm(request.POST, instance=ingredient)
        if form.is_valid():
            form.save()
            return redirect('recipe_detail', recipe_id=ingredient.recipe.id)
    else:
        form = RecipeIngredientForm(instance=ingredient)

    return render(
        request,
        'recipes/add_ingredient.html',
        {
            'form': form,
            'recipe': ingredient.recipe,
            'ingredient': ingredient,
            'page_title': 'Редактировать ингредиент',
            'submit_label': 'Сохранить изменения',
        },
    )


@login_required
def delete_recipe_ingredient_view(request, ingredient_id):
    ingredient = get_object_or_404(
        RecipeIngredient.objects.select_related('recipe'),
        pk=ingredient_id,
        recipe__author=request.user,
    )

    if request.method == 'POST':
        recipe_id = ingredient.recipe.id
        ingredient.delete()
        return redirect('recipe_detail', recipe_id=recipe_id)

    return render(
        request,
        'recipes/delete_ingredient.html',
        {'ingredient': ingredient, 'recipe': ingredient.recipe},
    )


@login_required
def api_products(request):
    not_auth = _api_ensure_auth(request)
    if not_auth is not None:
        return not_auth
    products = Product.objects.all().order_by('name')
    data = [
        {
            'id': product.id,
            'name': product.name,
            'calories_per_100g': int(product.calories_per_100g),
            'proteins': float(product.proteins),
            'fats': float(product.fats),
            'carbs': float(product.carbs),
        }
        for product in products
    ]
    return JsonResponse({'products': data})


def api_recipes(request):
    not_auth = _api_ensure_auth(request)
    if not_auth is not None:
        return not_auth
    recipes = _available_recipes_queryset(request.user)
    return JsonResponse({'recipes': [_serialize_recipe(r) for r in recipes]})


def api_recipe_detail(request, recipe_id: int):
    not_auth = _api_ensure_auth(request)
    if not_auth is not None:
        return not_auth
    recipe = _available_recipes_queryset(request.user).filter(pk=recipe_id).first()
    if recipe is None:
        return JsonResponse({'detail': 'Not found.'}, status=404)
    return JsonResponse(_serialize_recipe(recipe))
