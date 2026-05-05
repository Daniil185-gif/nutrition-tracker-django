from django.conf import settings
from django.db import models


class Recipe(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    photo = models.ImageField(upload_to='recipes/', blank=True, null=True)
    servings = models.PositiveIntegerField(default=1)
    cook_time_minutes = models.PositiveIntegerField(blank=True, null=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def total_calories(self):
        return sum(ingredient.calories() for ingredient in self.ingredients.all())

    def total_proteins(self):
        return sum(ingredient.proteins() for ingredient in self.ingredients.all())

    def total_fats(self):
        return sum(ingredient.fats() for ingredient in self.ingredients.all())

    def total_carbs(self):
        return sum(ingredient.carbs() for ingredient in self.ingredients.all())

    def total_weight(self):
        return sum(ingredient.grams for ingredient in self.ingredients.all())

    def calories_per_serving(self):
        if not self.servings:
            return 0
        return self.total_calories() / self.servings


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients',
    )
    name = models.CharField(max_length=255)
    grams = models.DecimalField(max_digits=8, decimal_places=2)
    calories_per_100g = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    proteins_per_100g = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    fats_per_100g = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    carbs_per_100g = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f'{self.name} - {self.grams}g'

    def calories(self):
        return self.calories_per_100g * self.grams / 100

    def proteins(self):
        return self.proteins_per_100g * self.grams / 100

    def fats(self):
        return self.fats_per_100g * self.grams / 100

    def carbs(self):
        return self.carbs_per_100g * self.grams / 100
