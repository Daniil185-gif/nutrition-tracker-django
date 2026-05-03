from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from diary.models import Product

from .models import Recipe, RecipeIngredient


class RecipeTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username='recipe_user',
            email='recipe@example.com',
            password='test-password',
        )
        self.product = Product.objects.create(
            name='Овсянка',
            calories_per_100g=350,
            proteins=12,
            fats=6,
            carbs=60,
            created_by=self.user,
        )
        self.recipe = Recipe.objects.create(
            title='Каша',
            description='Простая овсяная каша',
            author=self.user,
        )

    def test_recipe_total_calories(self):
        RecipeIngredient.objects.create(
            recipe=self.recipe,
            product=self.product,
            grams=200,
        )

        self.assertEqual(self.recipe.total_calories(), 700)

    def test_recipe_list_page_opens(self):
        response = self.client.get(reverse('recipe_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Каша')

    def test_recipe_detail_page_opens(self):
        response = self.client.get(
            reverse('recipe_detail', kwargs={'recipe_id': self.recipe.id}),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Каша')

    def test_logged_in_user_can_create_recipe(self):
        self.client.login(username='recipe_user', password='test-password')

        response = self.client.post(
            reverse('add_recipe'),
            {
                'title': 'Салат',
                'description': 'Лёгкий салат',
            },
        )

        recipe = Recipe.objects.get(title='Салат')
        self.assertRedirects(
            response,
            reverse('recipe_detail', kwargs={'recipe_id': recipe.id}),
        )
        self.assertEqual(recipe.author, self.user)

    def test_logged_in_author_can_add_recipe_ingredient(self):
        self.client.login(username='recipe_user', password='test-password')

        response = self.client.post(
            reverse('add_recipe_ingredient', kwargs={'recipe_id': self.recipe.id}),
            {
                'product': self.product.id,
                'grams': 150,
            },
        )

        self.assertRedirects(
            response,
            reverse('recipe_detail', kwargs={'recipe_id': self.recipe.id}),
        )
        self.assertTrue(
            RecipeIngredient.objects.filter(
                recipe=self.recipe,
                product=self.product,
                grams=150,
            ).exists(),
        )

    def test_products_api_returns_products(self):
        response = self.client.get(reverse('api_products'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['products'][0]['name'], 'Овсянка')

    def test_recipes_api_returns_recipes_with_ingredients(self):
        RecipeIngredient.objects.create(
            recipe=self.recipe,
            product=self.product,
            grams=100,
        )

        response = self.client.get(reverse('api_recipes'))

        recipe_data = response.json()['recipes'][0]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(recipe_data['title'], 'Каша')
        self.assertEqual(recipe_data['total_calories'], 350)
        self.assertEqual(recipe_data['ingredients'][0]['product'], 'Овсянка')
