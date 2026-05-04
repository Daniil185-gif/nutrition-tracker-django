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
    class Meta:
        model = FoodEntry
        fields = ('product', 'grams', 'meal', 'date')
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def save(self, commit=True, *, user=None):
        instance = super().save(commit=False)
        if user is not None:
            instance.user = user
        if commit:
            instance.save()
        return instance

