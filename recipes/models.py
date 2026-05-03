from django.conf import settings
from django.db import models

from diary.models import Product


class Recipe(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def total_calories(self):
        return sum(ingredient.calories() for ingredient in self.ingredients.all())


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
    )
    grams = models.PositiveIntegerField()

    class Meta:
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'product'],
                name='unique_product_in_recipe',
            ),
        ]

    def __str__(self):
        return f'{self.product.name} - {self.grams}g'

    def calories(self):
        return self.product.calories_per_100g * self.grams / 100
