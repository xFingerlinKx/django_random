from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory, APIClient

from .. import views
from ..models import Token


# coverage run --source='.' manage.py test test_api


class TestUserCreation(TestCase):

    def setUp(self) -> None:
        self.factory = APIRequestFactory()

        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin',
            password='admin',
        )
        self.token = Token.objects.get_or_create(user=self.admin)[0].key

    def test_user_create(self):
        request = self.factory.post(
            reverse('create-user'),
            {'username': 'new_user', 'password': 'test_password'},
            format='json',
            HTTP_AUTHORIZATION=f'Token {self.token}'
        )
        view = views.CreateUserAPIView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_token_is_active(self):
        request = self.factory.post(
            reverse('create-user'),
            {'username': 'new_user', 'password': 'test_password'},
            format='json',
            HTTP_AUTHORIZATION=f'Token {self.token}'
        )
        view = views.CreateUserAPIView.as_view()
        response = view(request)
        created_user = User.objects.get(username=response.data['username'])
        token = Token.objects.get_or_create(user=created_user)[0]
        self.assertTrue(token.is_active)


class UserLoginTest(TestCase):

    def setUp(self) -> None:
        self.url = reverse('api-token-auth')
        self.client = APIClient()
        self.factory = APIRequestFactory()

        self.username = 'test'
        self.password = 'test'

        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.token = Token.objects.get_or_create(user=self.user)[0].key

    def test_user_authentication(self):
        request = self.factory.post(
            self.url,
            {'username': self.username, 'password': self.password},
            format='json',
        )
        view = views.CustomAuthToken.as_view()
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.token, response.data['token'])
        self.assertEqual(self.user.id, response.data['user_id'])

    def test_user_authentication_no_credentials(self):
        required_data = {
            'username': ['This field is required.'],
            'password': ['This field is required.']
        }
        response = self.client.post(self.url, content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, required_data)

    def test_user_authentication_wrong_credentials(self):
        response = self.client.post(
            path=self.url,
            data={'username': self.username, 'password': 'wrong_password'},
            content_type='application/json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)

    def test_user_authentication_wrong_format(self):
        request = self.factory.post(
            self.url,
            {'username': self.username, 'password': self.password},
        )
        view = views.CustomAuthToken.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)


class TestUserLogout(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()

        self.url = reverse('api-token-logout')

        self.user = User.objects.create_user(
            username='test',
            password='test',
        )

    def test_user_logout_with_active_token(self):
        active_token = Token.objects.get_or_create(user=self.user)[0]
        request = self.factory.post(
            self.url,
            format='json',
            HTTP_AUTHORIZATION=f'Token {active_token}'
        )
        view = views.CustomAuthLogOut.as_view()
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_logout_with_not_active_token(self):
        invalid_tokens = ['']
        inactive_token = Token.objects.get_or_create(user=self.user)[0].is_active = False
        invalid_tokens.append(inactive_token)

        for token in invalid_tokens:
            request = self.factory.post(
                self.url,
                format='json',
                HTTP_AUTHORIZATION=f'Token {token}'
            )

            view = views.CustomAuthLogOut.as_view()
            response = view(request)

            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            self.assertNotEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(request.user.is_anonymous)
            self.assertFalse(request.user.is_authenticated)
