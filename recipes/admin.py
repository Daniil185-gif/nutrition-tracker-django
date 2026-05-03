from django.contrib import admin

from .models import Recipe, RecipeIngredient


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at')
    search_fields = ('title', 'author__username')
    list_filter = ('created_at',)
    inlines = (RecipeIngredientInline,)


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'product', 'grams')
    search_fields = ('recipe__title', 'product__name')
