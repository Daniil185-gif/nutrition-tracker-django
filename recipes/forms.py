from django import forms

from .models import Recipe, RecipeIngredient


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ('title', 'description')
        labels = {
            'title': 'Название',
            'description': 'Описание',
        }


class RecipeIngredientForm(forms.ModelForm):
    class Meta:
        model = RecipeIngredient
        fields = ('product', 'grams')
        labels = {
            'product': 'Продукт',
            'grams': 'Граммы',
        }
