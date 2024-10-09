from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from datetime import datetime
import pytz
from django.conf import settings
from recommendations.models import Item, Like
from users.models import User


class ItemAPITestCase(APITestCase):
    def setUp(self) -> None:
        self.user_owner = User.objects.create(email="test_owner@test.ru", password="test_password",
                                              phone="88005553535")
        self.standart_user = User.objects.create(email="test_standart@test.ru", password="test_password",
                                                 phone="88005553535")

        zone = pytz.timezone(settings.TIME_ZONE)
        self.now = datetime.now(zone)

        self.item = Item.objects.create(
            name="test",
            description="test",
            created_at=self.now,
            is_published=True,
            user=self.user_owner
        )

        self.like = Like.objects.create(user=self.standart_user, item=self.item)

    def test_item_list_anonymous_user(self):
        # Проверка для анонимного пользователя
        response = self.client.get(reverse('api_recommendations:api_item_list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['count'], 1)

    def test_item_list_authenticated_user(self):
        # Логин пользователя
        self.client.force_authenticate(user=self.standart_user)

        # Проверка для аутентифицированного пользователя
        response = self.client.get(reverse('api_recommendations:api_item_list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['count'], 1)

    def test_item_list_authenticated_user_own_item(self):
        # Логин владельца элемента
        self.client.force_authenticate(user=self.user_owner)

        response = self.client.get(reverse('api_recommendations:api_item_list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data['results']), 0)
        self.assertEqual(response.data['count'], 0)

    def test_item_retrieve(self):
        # Проверка доступа к элементу
        response = self.client.get(reverse('api_recommendations:api_item_detail', args=[self.item.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.item.name)

    def test_item_create_authenticated_user(self):
        self.client.force_authenticate(user=self.standart_user)
        data = {
            'name': 'new item',
            'description': 'new description',
            'created_at': self.now,
        }
        response = self.client.post(reverse('api_recommendations:api_item_create'), data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_item = Item.objects.get(pk=response.data['pk'])
        self.assertEqual(created_item.name, data['name'])
        self.assertEqual(created_item.user, self.standart_user)

    def test_item_update_authenticated_user_owner(self):
        self.client.force_authenticate(user=self.user_owner)
        data = {
            'name': 'updated item',
            'description': 'updated description',
        }
        response = self.client.put(reverse('api_recommendations:api_item_update', args=[self.item.id]), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.item.refresh_from_db()
        self.assertEqual(self.item.name, data['name'])

    def test_item_update_authenticated_user_not_owner(self):
        self.client.force_authenticate(user=self.standart_user)
        data = {
            'name': 'not allowed update',
            'description': 'should fail',
        }
        response = self.client.put(reverse('api_recommendations:api_item_update', args=[self.item.id]), data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_item_destroy_authenticated_user_owner(self):
        self.client.force_authenticate(user=self.user_owner)
        response = self.client.delete(reverse('api_recommendations:api_item_delete', args=[self.item.id]))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Item.objects.filter(id=self.item.id).exists())

    def test_item_destroy_authenticated_user_not_owner(self):
        self.client.force_authenticate(user=self.standart_user)
        response = self.client.delete(reverse('api_recommendations:api_item_delete', args=[self.item.id]))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_name_should_not_contain_stop_word(self):
        self.client.force_authenticate(user=self.user_owner)
        data = {
            'name': 'This is a name with казино',
            'description': 'This is a valid description'
        }
        response = self.client.post(reverse('api_recommendations:api_item_create'), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'non_field_errors': ['Слово "казино" недопустимо!']})

    def test_description_should_not_contain_stop_word(self):
        self.client.force_authenticate(user=self.user_owner)
        data = {
            'name': 'This is a valid name',
            'description': 'This description contains казино'
        }
        response = self.client.post(reverse('api_recommendations:api_item_create'), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'non_field_errors': ['Слово "казино" недопустимо!']})

    def test_user_item_list_with_pagination(self):
        for i in range(3):
            Item.objects.create(
                name=f"test item {i}",
                description="test description",
                created_at=self.now,
                is_published=True,
                user=self.user_owner
            )

        self.client.force_authenticate(user=self.user_owner)
        response = self.client.get(reverse('api_recommendations:api_user_item_list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 4)
        self.assertEqual(response.data['count'], 4)

    def test_user_item_list_no_items(self):
        self.client.force_authenticate(user=self.standart_user)
        response = self.client.get(reverse('api_recommendations:api_user_item_list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)
        self.assertEqual(response.data['count'], 0)

    def test_recommended_items(self):
        self.client.force_authenticate(user=self.standart_user)
        response = self.client.get(reverse('api_recommendations:api_item_recommended'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)
        self.assertEqual(response.data['count'], 0)

    def test_recommended_items_user_without_like_set(self):
        self.client.force_authenticate(user=self.user_owner)
        response = self.client.get(reverse('api_recommendations:api_item_recommended'))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_statistic_view(self):
        self.client.force_authenticate(user=self.standart_user)
        response = self.client.get(reverse('api_recommendations:api_statistic'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_statistic_view_user_without_like_set(self):
        self.client.force_authenticate(user=self.user_owner)
        response = self.client.get(reverse('api_recommendations:api_statistic'))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class LikeAPITestCase(APITestCase):
    def setUp(self) -> None:
        self.user_owner = User.objects.create(email="test_owner@test.ru", password="test_password",
                                              phone="88005553535")
        self.standart_user = User.objects.create(email="test_standart@test.ru", password="test_password",
                                                 phone="88005553535")

        zone = pytz.timezone(settings.TIME_ZONE)
        self.now = datetime.now(zone)

        self.item = Item.objects.create(
            name="test",
            description="test",
            created_at=self.now,
            is_published=True,
            user=self.user_owner
        )

        self.like = Like.objects.create(user=self.standart_user, item=self.item)

    def test_user_like_list_with_pagination(self):
        self.client.force_authenticate(user=self.standart_user)
        response = self.client.get(reverse('api_recommendations:api_user_like_list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['count'], 1)

    def test_user_like_list_no_likes(self):
        self.client.force_authenticate(user=self.user_owner)
        response = self.client.get(reverse('api_recommendations:api_user_like_list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)
        self.assertEqual(response.data['count'], 0)

    def test_like_item_success(self):
        item = Item.objects.create(name="test", description="test", created_at=self.now,
                                   is_published=True, user=self.user_owner)

        self.client.force_authenticate(user=self.standart_user)
        data = {
            'item': item.pk
        }
        response = self.client.post(reverse('api_recommendations:api_item_like'), data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user'], self.standart_user.pk)
        item.refresh_from_db()
        self.assertEqual(item.count_likes, 1)

    def test_like_item_already_liked(self):
        self.client.force_authenticate(user=self.standart_user)

        data = {
            'item': self.item.pk
        }
        response = self.client.post(reverse('api_recommendations:api_item_like'), data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('Error', response.data)
        self.assertEqual(response.data['Error'],
                         "Вы не можете лайкать свои элементы и не можете поставить лайк второй раз!")

    def test_like_item_owner(self):
        self.client.force_authenticate(user=self.user_owner)
        data = {
            'item': self.item.pk
        }
        response = self.client.post(reverse('api_recommendations:api_item_like'), data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('Error', response.data)
        self.assertEqual(response.data['Error'],
                         "Вы не можете лайкать свои элементы и не можете поставить лайк второй раз!")

    def test_unlike_item_success(self):
        self.client.force_authenticate(user=self.standart_user)

        data = {
            'item': self.item.pk
        }
        response = self.client.delete(reverse('api_recommendations:api_item_unlike'), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['Message'], "Лайк успешно убран!")
        self.item.refresh_from_db()
        self.assertEqual(self.item.count_likes, -1)

    def test_unlike_item_not_liked(self):
        item = Item.objects.create(name="test", description="test", created_at=self.now,
                                   is_published=True, user=self.user_owner)

        self.client.force_authenticate(user=self.standart_user)

        data = {
            'item': item.pk
        }
        response = self.client.delete(reverse('api_recommendations:api_item_unlike'), data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
