from django.contrib import admin

from .models import FoodEntry, Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'calories_per_100g', 'proteins', 'fats', 'carbs')
    search_fields = ('name',)


@admin.register(FoodEntry)
class FoodEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'grams', 'meal', 'date', 'created_at')
    list_filter = ('meal', 'date')
    search_fields = ('user__username', 'product__name')
