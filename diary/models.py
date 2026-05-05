from django.conf import settings
from django.db import models
from django.db.models import Q
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Product(models.Model):
    name = models.CharField(max_length=255, unique=True)
    calories_per_100g = models.PositiveIntegerField()
    proteins = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    fats = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    carbs = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='created_products',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class FoodEntry(models.Model):
    class MealChoices(models.TextChoices):
        BREAKFAST = 'breakfast', 'Завтрак'
        LUNCH = 'lunch', 'Обед'
        DINNER = 'dinner', 'Ужин'
        SNACK = 'snack', 'Перекус'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='food_entries',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='food_entries',
        blank=True,
        null=True,
    )
    grams = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    recipe_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name='recipe_food_entries',
    )
    recipe_object_id = models.PositiveIntegerField(blank=True, null=True)
    recipe = GenericForeignKey('recipe_content_type', 'recipe_object_id')
    servings = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        help_text='Сколько порций рецепта было съедено (например 1.00).',
    )
    meal = models.CharField(max_length=20, choices=MealChoices.choices)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']
        constraints = [
            models.CheckConstraint(
                name='foodentry_product_xor_recipe',
                check=(
                    (Q(product__isnull=False) & Q(recipe_content_type__isnull=True) & Q(recipe_object_id__isnull=True))
                    | (Q(product__isnull=True) & Q(recipe_content_type__isnull=False) & Q(recipe_object_id__isnull=False))
                ),
            ),
            models.CheckConstraint(
                name='foodentry_grams_required_for_product',
                check=Q(product__isnull=True) | Q(grams__isnull=False),
            ),
            models.CheckConstraint(
                name='foodentry_servings_required_for_recipe',
                check=Q(recipe_content_type__isnull=True) | Q(servings__isnull=False),
            ),
        ]

    def __str__(self):
        if self.product_id:
            return f'{self.user} — {self.product} ({self.grams} г) — {self.date}'
        return f'{self.user} — рецепт ({self.servings} порц.) — {self.date}'
