from django import forms

from .models import Recipe, RecipeIngredient


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ('title', 'description', 'photo', 'servings', 'cook_time_minutes')
        labels = {
            'title': 'Название',
            'description': 'Описание',
            'photo': 'Фото',
            'servings': 'Количество порций',
            'cook_time_minutes': 'Время приготовления (мин)',
        }


class RecipeIngredientForm(forms.ModelForm):
    class Meta:
        model = RecipeIngredient
        fields = (
            'name',
            'grams',
            'calories_per_100g',
            'proteins_per_100g',
            'fats_per_100g',
            'carbs_per_100g',
        )
        labels = {
            'name': 'Ингредиент',
            'grams': 'Граммы',
            'calories_per_100g': 'Калории на 100 г',
            'proteins_per_100g': 'Белки на 100 г',
            'fats_per_100g': 'Жиры на 100 г',
            'carbs_per_100g': 'Углеводы на 100 г',
        }
