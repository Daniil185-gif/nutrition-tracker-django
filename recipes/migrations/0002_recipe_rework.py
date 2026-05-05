from decimal import Decimal

from django.db import migrations, models
import django.utils.timezone


def copy_product_data_to_ingredients(apps, schema_editor):
    RecipeIngredient = apps.get_model('recipes', 'RecipeIngredient')

    for ingredient in RecipeIngredient.objects.select_related('product').all():
        product = ingredient.product
        ingredient.name = product.name
        ingredient.calories_per_100g = Decimal(product.calories_per_100g)
        ingredient.proteins_per_100g = product.proteins
        ingredient.fats_per_100g = product.fats
        ingredient.carbs_per_100g = product.carbs
        ingredient.save(
            update_fields=[
                'name',
                'calories_per_100g',
                'proteins_per_100g',
                'fats_per_100g',
                'carbs_per_100g',
            ],
        )


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='cook_time_minutes',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='recipe',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='recipes/'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='servings',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='recipe',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='recipeingredient',
            name='calories_per_100g',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
        migrations.AddField(
            model_name='recipeingredient',
            name='carbs_per_100g',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
        migrations.AddField(
            model_name='recipeingredient',
            name='fats_per_100g',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
        migrations.AddField(
            model_name='recipeingredient',
            name='name',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='recipeingredient',
            name='proteins_per_100g',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
        migrations.RunPython(copy_product_data_to_ingredients, migrations.RunPython.noop),
        migrations.RemoveConstraint(
            model_name='recipeingredient',
            name='unique_product_in_recipe',
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='grams',
            field=models.DecimalField(decimal_places=2, max_digits=8),
        ),
        migrations.RemoveField(
            model_name='recipeingredient',
            name='product',
        ),
    ]
