#Triple A
#Arrange - подготовка данных
#Act - совершение действия (вызов функции, класса, запрос)
#Assert - проверка результатов

# def factorial(number):
#     fact = 1
#     for i in range(1, number + 1):
#         fact *= i
#     return fact
#
# factorial(10)
# num1 = 10
# expected_value = 3628800
#
# assert factorial(num1) == expected_value
# assert factorial(9) == 362880

# Uni Test

from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from .models import Product, ProductReview
from rest_framework.test import APIClient, APITestCase

User = get_user_model()

class TestProduct(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user('test@gmail.com',
                                             'qwerty',
                                             name='User1',
                                             is_active=True)

        self.admin = User.objects.create_superuser('admin@gmail.com',
                                                   'qwerty',
                                                   name='Admin1')

        self.user_token = Token.objects.create(user=self.user)
        self.admin_token = Token.objects.create(user=self.admin)
        self.product1 = Product.objects.create(title='Apple Iphone 12',
                                               description='overpriced',
                                               price=100000)
        self.product2 = Product.objects.create(title='Apple MacBook Pro',
                                               description='notebook for work',
                                               price=200000)
        self.product3 = Product.objects.create(title='Samsung Galaxy S20',
                                               description='price quality',
                                               price=90000)
        self.product4 = Product.objects.create(title='Xiaomi Mi 12',
                                               description='overpriced',
                                               price=40000)

        self.product_payload = {
            'title': 'Acer Aspire E15',
            'description': 'Low price laptop',
            'price': 18000
        }

    def test_list(self):
        client = APIClient()
        url = reverse('product-list')
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 4)

    def test_create_product_as_anonymous_user(self):
        client = APIClient()
        url = reverse('product-list')
        response = client.post(url, data=self.product_payload)
        self.assertEqual(response.status_code, 401)

    def test_create_product_as_regular_user(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
        url = reverse('product-list')
        response = client.post(url, data=self.product_payload)
        self.assertEqual(response.status_code, 403)

    def test_create_product_as_admin(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        url = reverse('product-list')
        response = client.post(url, data=self.product_payload)
        self.assertEqual(response.status_code, 201)

    def test_create_product_without_title(self):
        data = self.product_payload.copy()
        data.pop('title')
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        url = reverse('product-list')
        response = client.post(url, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('title', response.data)

    def test_create_product_without_description(self):
        data = self.product_payload.copy()
        data.pop('description')
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        url = reverse('product-list')
        response = client.post(url, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('description', response.data)

    def test_create_product_without_price(self):
        data = self.product_payload.copy()
        data.pop('price')
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        url = reverse('product-list')
        response = client.post(url, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('price', response.data)

    def test_create_product_with_negative_price(self):
        data = self.product_payload.copy()
        data['price'] = -10000
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        url = reverse('product-list')
        response = client.post(url, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('price', response.data)

    def test_details(self):
        prod_id = self.product1.id
        client = APIClient()
        url = reverse('product-detail', args=(prod_id, ))
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], self.product1.title)

    def test_update(self):
        prod2_id = self.product2.id
        new_price = '175000.00'
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        url = reverse('product-detail', args=(prod2_id,))
        response = client.patch(url, {'price': new_price})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['price'], new_price)

    def test_delete(self):
        prod2_id = self.product2.id
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        url = reverse('product-detail', args=(prod2_id,))
        response = client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertIs(response.data, None)

    def test_filtering_by_price(self):
        client = APIClient()
        url = reverse('product-list')
        params = {'price_from': 50000}
        response = client.get(url, data=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 3)
        first_price = response.data['results'][0]['price']
        self.assertGreaterEqual(float(first_price), 50000)

    def test_search(self):
        client = APIClient()
        url = reverse('product-list')
        params = {'search': 'apple'}
        response = client.get(url, data=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 2)

    def test_ordering(self):
        client = APIClient()
        url = reverse('product-list')
        params = {'ordering': '-price'}
        response = client.get(url, data=params)
        self.assertEqual(response.status_code, 200)
        first_id = response.data['results'][0]['id']
        self.assertEqual(first_id, self.product2.id)

class TestReviews(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user('test@gmail.com',
                                             'qwerty',
                                             name='User1',
                                             is_active=True)

        self.user2 = User.objects.create_user('test2@gmail.com',
                                             'qwerty',
                                             name='User2',
                                             is_active=True)

        self.admin = User.objects.create_superuser('admin@gmail.com',
                                                   'qwerty',
                                                   name='Admin1')

        self.user_token = Token.objects.create(user=self.user)
        self.user2_token = Token.objects.create(user=self.user2)
        self.admin_token = Token.objects.create(user=self.admin)


        self.product1 = Product.objects.create(title='Apple Iphone 12',
                                               description='overpriced',
                                               price=100000)
        self.product2 = Product.objects.create(title='Apple MacBook Pro',
                                               description='notebook for work',
                                               price=200000)
        self.product3 = Product.objects.create(title='Samsung Galaxy S20',
                                               description='price quality',
                                               price=90000)
        self.product4 = Product.objects.create(title='Xiaomi Mi 12',
                                               description='overpriced',
                                               price=40000)

        self.review1 = ProductReview.objects.create(
            product=self.product1,
            author=self.user,
            text='good phone',
            rating=3
        )

        self.review1 = ProductReview.objects.create(
            product=self.product2,
            author=self.user,
            text='very good phone',
            rating=5
        )

        self.payload = {
            'product': self.product3.id,
            'text': 'positive review',
            'rating': 4
        }

    def test_create_review_by_anonymous_user(self):
        client = self.client_class()
        url = reverse('productreview-list')
        response = client.post(url, data=self.payload)
        self.assertEqual(response.status_code, 401)

    def test_create_review_by_regular_user(self):
        client = self.client_class()
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
        url = reverse('productreview-list')
        response = client.post(url, data=self.payload)
        self.assertEqual(response.status_code, 201)

    def test_create_review_duplicate(self):
        data = self.payload.copy()
        data['product'] = self.product1.id
        client = self.client_class()
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
        url = reverse('productreview-list')
        response = client.post(url, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('product', response.data)

    def test_create_review_with_wrong_rating(self):
        '''Тест проверяет создание отзыва с рейтингом выше 5'''
        data = self.payload.copy()
        data['rating'] = 100
        client = self.client_class()
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.user2_token.key}')
        url = reverse('productreview-list')
        response = client.post(url, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('rating', response.data)

    def test_create_review_with_negative_rating(self):
        data = self.payload.copy()
        data['rating'] = -10
        client = self.client_class()
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.user2_token.key}')
        url = reverse('productreview-list')
        response = client.post(url, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('rating', response.data)

    def test_create_review_with_rating(self):
        data = self.payload.copy()
        data['rating'] = 4
        client = self.client_class()
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
        url = reverse('productreview-list')
        response = client.post(url, data=data)
        self.assertEqual(response.status_code, 201)
        self.assertIn('rating', response.data)

    def test_update_review_as_anounymous_user(self):
        client = self.client_class()
        url = reverse('productreview-detail', args=(self.review1.id,))
        data = {'text': 'new_text'}
        response = client.patch(url, data)
        self.assertEqual(response.status_code, 401)

    def test_update_review_as_not_author(self):
        client = self.client_class()
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.user2_token.key}')
        url = reverse('productreview-detail', args=(self.review1.id,))
        data = {'text': 'new_text'}
        response = client.patch(url, data)
        self.assertEqual(response.status_code, 403)

    def test_updates_review_as_admin(self):
        client = self.client_class()
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        url = reverse('productreview-detail', args=(self.review1.id,))
        data = {'text': 'new_text'}
        response = client.patch(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual('new_text', response.data['text'])

    def test_updates_review_as_admin(self):
        client = self.client_class()
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
        url = reverse('productreview-detail', args=(self.review1.id,))
        data = {'text': 'new_text'}
        response = client.patch(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual('new_text', response.data['text'])

#TODO pytest
#TODO фабрика данных test factory, factory boy, model bakery
#TODO фикстура
#TODO breakpoint