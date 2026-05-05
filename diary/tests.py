from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import FoodEntry, Product
from recipes.models import Recipe, RecipeIngredient


class FoodEntryTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username='diary_user',
            email='diary@example.com',
            password='test-password',
        )
        self.product = Product.objects.create(
            name='Печенье Oreo',
            calories_per_100g=480,
            proteins=5,
            fats=20,
            carbs=70,
            created_by=self.user,
        )

    def test_add_food_entry_page_opens(self):
        self.client.login(username='diary_user', password='test-password')

        response = self.client.get(reverse('add_food_entry'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'diary/add_food_entry.html')

    def test_logged_in_user_can_add_food_entry(self):
        self.client.login(username='diary_user', password='test-password')

        response = self.client.post(
            reverse('add_food_entry'),
            {
                'product': self.product.id,
                'grams': '60',
                'meal': FoodEntry.MealChoices.SNACK,
                'date': '2026-05-04',
            },
        )

        self.assertRedirects(response, f"{reverse('diary')}?date=2026-05-04")
        self.assertTrue(
            FoodEntry.objects.filter(
                user=self.user,
                product=self.product,
                grams=60,
                meal=FoodEntry.MealChoices.SNACK,
                date='2026-05-04',
            ).exists(),
        )

    def test_logged_in_user_can_add_recipe_entry(self):
        recipe = Recipe.objects.create(
            title='Омлет',
            description='Сырный омлет',
            author=self.user,
            servings=2,
            cook_time_minutes=10,
        )
        RecipeIngredient.objects.create(
            recipe=recipe,
            name='Яйцо',
            grams=100,
            calories_per_100g=155,
            proteins_per_100g=13,
            fats_per_100g=11,
            carbs_per_100g=1.1,
        )

        self.client.login(username='diary_user', password='test-password')
        response = self.client.post(
            reverse('add_food_entry'),
            {
                'recipe': recipe.id,
                'servings': '1.00',
                'meal': FoodEntry.MealChoices.BREAKFAST,
                'date': '2026-05-04',
            },
        )

        self.assertRedirects(response, f"{reverse('diary')}?date=2026-05-04")
        self.assertTrue(
            FoodEntry.objects.filter(
                user=self.user,
                product__isnull=True,
                recipe_object_id=recipe.id,
                servings='1.00',
                meal=FoodEntry.MealChoices.BREAKFAST,
                date='2026-05-04',
            ).exists(),
        )

    def test_diary_shows_nutrition_totals_and_user_norms(self):
        self.user.profile.weight_kg = 70
        self.user.profile.daily_calorie_goal = 2200
        self.user.profile.save()
        FoodEntry.objects.create(
            user=self.user,
            product=self.product,
            grams=50,
            meal=FoodEntry.MealChoices.SNACK,
            date='2026-05-04',
        )
        self.client.login(username='diary_user', password='test-password')

        response = self.client.get(f"{reverse('diary')}?date=2026-05-04")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '240 / 2200 ккал')
        self.assertContains(response, '2,5 / 112,0 г')
        self.assertContains(response, '10,0 / 56,0 г')
