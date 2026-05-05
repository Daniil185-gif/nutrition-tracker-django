from django.urls import path

from .views import (
    add_recipe_ingredient_view,
    add_recipe_view,
    api_products,
    api_recipes,
    delete_recipe_ingredient_view,
    delete_recipe_view,
    edit_recipe_ingredient_view,
    edit_recipe_view,
    recipe_detail_view,
    recipe_list_view,
)

urlpatterns = [
    path('recipes/', recipe_list_view, name='recipe_list'),
    path('recipes/add/', add_recipe_view, name='add_recipe'),
    path('recipes/<int:recipe_id>/', recipe_detail_view, name='recipe_detail'),
    path('recipes/<int:recipe_id>/edit/', edit_recipe_view, name='edit_recipe'),
    path('recipes/<int:recipe_id>/delete/', delete_recipe_view, name='delete_recipe'),
    path(
        'recipes/<int:recipe_id>/ingredients/add/',
        add_recipe_ingredient_view,
        name='add_recipe_ingredient',
    ),
    path(
        'recipes/ingredients/<int:ingredient_id>/edit/',
        edit_recipe_ingredient_view,
        name='edit_recipe_ingredient',
    ),
    path(
        'recipes/ingredients/<int:ingredient_id>/delete/',
        delete_recipe_ingredient_view,
        name='delete_recipe_ingredient',
    ),
    path('api/products/', api_products, name='api_products'),
    path('api/recipes/', api_recipes, name='api_recipes'),
]
