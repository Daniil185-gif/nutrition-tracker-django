from django import forms

from .models import FoodEntry, Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ('name', 'calories_per_100g', 'proteins', 'fats', 'carbs')

    def save(self, commit=True, *, created_by=None):
        instance = super().save(commit=False)
        if created_by is not None and instance.created_by_id is None:
            instance.created_by = created_by
        if commit:
            instance.save()
        return instance


class FoodEntryForm(forms.ModelForm):
    recipe = forms.ModelChoiceField(
        queryset=None,
        required=False,
        label='Рецепт',
    )

    class Meta:
        model = FoodEntry
        fields = ('product', 'grams', 'meal', 'date', 'servings')
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Avoid hard dependency in migrations; runtime import is fine.
        from recipes.models import Recipe  # noqa: PLC0415

        self.fields['recipe'].queryset = Recipe.objects.all().order_by('-created_at')
        if user is not None:
            self._user = user

        self.fields['servings'].label = 'Порции (для рецепта)'

    def clean(self):
        cleaned = super().clean()
        product = cleaned.get('product')
        grams = cleaned.get('grams')
        recipe = cleaned.get('recipe')
        servings = cleaned.get('servings')

        if product and recipe:
            raise forms.ValidationError('Нельзя выбрать одновременно продукт и рецепт — выберите что-то одно.')
        if not product and not recipe:
            raise forms.ValidationError('Нужно выбрать продукт или рецепт.')

        if product and grams is None:
            self.add_error('grams', 'Укажите граммы для продукта.')
        if recipe and servings is None:
            self.add_error('servings', 'Укажите количество порций для рецепта.')

        return cleaned

    def save(self, commit=True, *, user=None):
        instance = super().save(commit=False)
        if user is not None:
            instance.user = user

        recipe = self.cleaned_data.get('recipe')
        if recipe is not None:
            from django.contrib.contenttypes.models import ContentType  # noqa: PLC0415

            instance.product = None
            instance.grams = None
            instance.recipe_content_type = ContentType.objects.get_for_model(recipe)
            instance.recipe_object_id = recipe.pk
        if commit:
            instance.save()
        return instance

