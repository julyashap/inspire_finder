from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from users.models import User
from api_users.serializers import UserSerializer, AnotherUserSerializer


class UserAPITestCase(APITestCase):
    """Класс тестирования API-контроллеров модели User"""

    def setUp(self):
        self.user = User.objects.create(email="user@test.com", phone="88005553535", password="test_password")
        self.another_user = User.objects.create(email="another_user@test.com", phone="88005553535",
                                                password="test_password")

    def test_user_create(self):
        data = {
            'email': 'new_user@test.com',
            'password': 'new_password',
            'phone': '88005553535'
        }
        response = self.client.post(reverse('api_users:api_user_create'), data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3)

    def test_user_update(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'email': 'updated_user@test.com'
        }
        response = self.client.patch(reverse('api_users:api_user_update', args=[self.user.pk]), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'updated_user@test.com')

    def test_user_update_other_user(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'email': 'malicious_user@test.com'
        }
        response = self.client.patch(reverse('api_users:api_user_update', args=[self.another_user.pk]), data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_retrieve_self(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('api_users:api_user_retrieve', args=[self.user.pk]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = UserSerializer(self.user)
        self.assertEqual(response.data, serializer.data)

    def test_user_retrieve_other_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('api_users:api_user_retrieve', args=[self.another_user.pk]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = AnotherUserSerializer(self.another_user)
        self.assertEqual(response.data, serializer.data)

    def test_user_destroy_self(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(reverse('api_users:api_user_destroy', args=[self.user.pk]))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(), 1)

    def test_user_destroy_other_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(reverse('api_users:api_user_destroy', args=[self.another_user.pk]))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
