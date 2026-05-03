from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from diary.models import Product

from .forms import RecipeForm, RecipeIngredientForm
from .models import Recipe


def recipe_list_view(request):
    recipes = Recipe.objects.select_related('author').prefetch_related(
        'ingredients__product',
    )
    return render(request, 'recipes/recipe_list.html', {'recipes': recipes})


def recipe_detail_view(request, recipe_id):
    recipe = get_object_or_404(
        Recipe.objects.select_related('author').prefetch_related(
            'ingredients__product',
        ),
        pk=recipe_id,
    )
    return render(request, 'recipes/recipe_detail.html', {'recipe': recipe})


@login_required
def add_recipe_view(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()
            return redirect('recipe_detail', recipe_id=recipe.id)
    else:
        form = RecipeForm()

    return render(request, 'recipes/add_recipe.html', {'form': form})


@login_required
def add_recipe_ingredient_view(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)

    if recipe.author != request.user:
        return redirect('recipe_detail', recipe_id=recipe.id)

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
    }
    return render(request, 'recipes/add_ingredient.html', context)


def api_products(request):
    products = Product.objects.all()
    data = [
        {
            'id': product.id,
            'name': product.name,
            'calories_per_100g': product.calories_per_100g,
            'proteins': float(product.proteins),
            'fats': float(product.fats),
            'carbs': float(product.carbs),
        }
        for product in products
    ]
    return JsonResponse({'products': data})


def api_recipes(request):
    recipes = Recipe.objects.select_related('author').prefetch_related(
        'ingredients__product',
    )
    data = [
        {
            'id': recipe.id,
            'title': recipe.title,
            'description': recipe.description,
            'author': recipe.author.username,
            'total_calories': recipe.total_calories(),
        }
        for recipe in recipes
    ]
    return JsonResponse({'recipes': data})
