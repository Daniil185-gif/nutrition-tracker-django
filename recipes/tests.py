from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import Recipe, RecipeIngredient


class RecipeTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.author = user_model.objects.create_user(
            username='recipe_author',
            email='author@example.com',
            password='test-password',
        )
        self.friend = user_model.objects.create_user(
            username='recipe_friend',
            email='friend@example.com',
            password='test-password',
        )
        self.other_user = user_model.objects.create_user(
            username='recipe_other',
            email='other@example.com',
            password='test-password',
        )
        self.author.friends.add(self.friend)
        self.recipe = Recipe.objects.create(
            title='Куриная тарелка',
            description='Сытный рецепт',
            author=self.author,
            servings=2,
            cook_time_minutes=25,
        )
        self.ingredient = RecipeIngredient.objects.create(
            recipe=self.recipe,
            name='Курица',
            grams=200,
            calories_per_100g=165,
            proteins_per_100g=31,
            fats_per_100g=3.6,
            carbs_per_100g=0,
        )

    def test_recipe_totals_are_calculated(self):
        self.assertEqual(self.recipe.total_calories(), 330)
        self.assertEqual(self.recipe.total_proteins(), 62)
        self.assertEqual(float(self.recipe.total_fats()), 7.2)
        self.assertEqual(self.recipe.total_carbs(), 0)

    def test_friend_can_see_recipe(self):
        self.client.login(username='recipe_friend', password='test-password')
        response = self.client.get(reverse('recipe_detail', kwargs={'recipe_id': self.recipe.id}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Куриная тарелка')

    def test_non_friend_cannot_see_recipe(self):
        self.client.login(username='recipe_other', password='test-password')
        response = self.client.get(reverse('recipe_detail', kwargs={'recipe_id': self.recipe.id}))

        self.assertRedirects(response, reverse('recipe_list'))

    def test_author_can_create_recipe_with_photo(self):
        self.client.login(username='recipe_author', password='test-password')
        image = SimpleUploadedFile(
            'recipe.jpg',
            (
                b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00'
                b'\x00\x00\x00\xff\xff\xff\x21\xf9\x04\x01\x00\x00\x00\x00'
                b'\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
            ),
            content_type='image/gif',
        )
        response = self.client.post(
            reverse('add_recipe'),
            {
                'title': 'Омлет',
                'description': 'Сырный омлет',
                'servings': 1,
                'cook_time_minutes': 10,
                'photo': image,
            },
        )

        recipe = Recipe.objects.get(title='Омлет')
        self.assertRedirects(response, reverse('recipe_detail', kwargs={'recipe_id': recipe.id}))
        self.assertEqual(recipe.author, self.author)
        self.assertTrue(bool(recipe.photo))

    def test_author_can_edit_recipe(self):
        self.client.login(username='recipe_author', password='test-password')
        response = self.client.post(
            reverse('edit_recipe', kwargs={'recipe_id': self.recipe.id}),
            {
                'title': 'Обновлённый рецепт',
                'description': 'Новое описание',
                'servings': 3,
                'cook_time_minutes': 40,
            },
        )

        self.recipe.refresh_from_db()
        self.assertRedirects(response, reverse('recipe_detail', kwargs={'recipe_id': self.recipe.id}))
        self.assertEqual(self.recipe.title, 'Обновлённый рецепт')
        self.assertEqual(self.recipe.servings, 3)

    def test_author_can_delete_recipe(self):
        self.client.login(username='recipe_author', password='test-password')
        response = self.client.post(reverse('delete_recipe', kwargs={'recipe_id': self.recipe.id}))

        self.assertRedirects(response, reverse('recipe_list'))
        self.assertFalse(Recipe.objects.filter(pk=self.recipe.id).exists())

    def test_author_can_manage_ingredients(self):
        self.client.login(username='recipe_author', password='test-password')
        add_response = self.client.post(
            reverse('add_recipe_ingredient', kwargs={'recipe_id': self.recipe.id}),
            {
                'name': 'Рис',
                'grams': 150,
                'calories_per_100g': 130,
                'proteins_per_100g': 2.7,
                'fats_per_100g': 0.3,
                'carbs_per_100g': 28,
            },
        )
        ingredient = RecipeIngredient.objects.get(recipe=self.recipe, name='Рис')
        edit_response = self.client.post(
            reverse('edit_recipe_ingredient', kwargs={'ingredient_id': ingredient.id}),
            {
                'name': 'Рис басмати',
                'grams': 180,
                'calories_per_100g': 130,
                'proteins_per_100g': 2.7,
                'fats_per_100g': 0.3,
                'carbs_per_100g': 28,
            },
        )
        delete_response = self.client.post(
            reverse('delete_recipe_ingredient', kwargs={'ingredient_id': ingredient.id}),
        )

        self.assertRedirects(add_response, reverse('recipe_detail', kwargs={'recipe_id': self.recipe.id}))
        self.assertRedirects(edit_response, reverse('recipe_detail', kwargs={'recipe_id': self.recipe.id}))
        self.assertRedirects(delete_response, reverse('recipe_detail', kwargs={'recipe_id': self.recipe.id}))
        self.assertFalse(RecipeIngredient.objects.filter(pk=ingredient.id).exists())

    def test_recipes_api_returns_recipe_macros(self):
        self.client.login(username='recipe_friend', password='test-password')
        response = self.client.get(reverse('api_recipes'))

        recipe_data = response.json()['recipes'][0]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(recipe_data['title'], 'Куриная тарелка')
        self.assertEqual(recipe_data['ingredients'][0]['name'], 'Курица')
        self.assertEqual(recipe_data['total_calories'], 330.0)

    def test_recipes_api_requires_auth(self):
        response = self.client.get(reverse('api_recipes'))
        self.assertEqual(response.status_code, 401)

    def test_products_api_requires_auth(self):
        response = self.client.get(reverse('api_products'))
        self.assertEqual(response.status_code, 401)

    def test_recipe_detail_api_returns_recipe_for_friend(self):
        self.client.login(username='recipe_friend', password='test-password')
        response = self.client.get(reverse('api_recipe_detail', kwargs={'recipe_id': self.recipe.id}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['id'], self.recipe.id)
        self.assertEqual(response.json()['title'], 'Куриная тарелка')

    def test_recipe_detail_api_returns_404_for_non_friend(self):
        self.client.login(username='recipe_other', password='test-password')
        response = self.client.get(reverse('api_recipe_detail', kwargs={'recipe_id': self.recipe.id}))

        self.assertEqual(response.status_code, 404)

    def test_recipe_detail_api_requires_auth(self):
        response = self.client.get(reverse('api_recipe_detail', kwargs={'recipe_id': self.recipe.id}))
        self.assertEqual(response.status_code, 401)
