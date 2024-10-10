from datetime import datetime
import networkx as nx
import pytz
from django.contrib.auth import authenticate
from django.core import mail
from django.template.response import TemplateResponse
from django.urls import reverse
from django.test import TestCase
from config import settings
from users.models import User
from .models import Category, Item, Like
from .services import get_statistics, collaborative_filtering_alg, get_same_interest_users, kNN_alg, create_likes_graph, \
    page_rank_alg


class ItemCategoryTestCase(TestCase):
    """Класс тестирования контроллеров моделей Item и Category"""

    def setUp(self):
        self.user_owner = User.objects.create(email='user_owner@test.com', password='password', phone="88005553535")
        self.user = User.objects.create(email='user@test.com', password='password', phone="88005553535")

        self.category_1 = Category.objects.create(name="test1", description="test")

        zone = pytz.timezone(settings.TIME_ZONE)
        self.now = datetime.now(zone)

        self.item_1 = Item.objects.create(
            name="test1",
            description="test",
            created_at=self.now,
            is_published=True,
            user=self.user_owner,
            category=self.category_1
        )
        self.item_2 = Item.objects.create(
            name="test2",
            description="test",
            created_at=self.now,
            is_published=True,
            user=self.user_owner,
            category=self.category_1
        )

        self.like_1 = Like.objects.create(user=self.user, item=self.item_1)

    def test_category_list_view(self):
        response = self.client.get(reverse('recommendations:category_list'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['object_list'],
            [self.category_1],
            ordered=False
        )

    def test_filtered_category_list_view(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('recommendations:category_list'), {'search': '2'})
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['object_list'],
            [],
            ordered=False
        )

    def test_user_item_list_view(self):
        self.client.force_login(self.user_owner)

        response = self.client.get(reverse('recommendations:user_item_list'))
        self.assertEqual(response.status_code, 200)

        self.assertQuerysetEqual(
            response.context['object_list'],
            [self.item_2, self.item_1],
            ordered=False
        )

    def test_item_list_view_authenticated_with_query(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('recommendations:item_list', args=[self.category_1.pk]), {'search': '1'})

        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['object_list'], [self.item_1], ordered=False)

    def test_item_list_view_authenticated_without_query(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('recommendations:item_list', args=[self.category_1.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['object_list'], [self.item_1, self.item_2], ordered=False)

    def test_item_list_view_not_authenticated_with_query(self):
        response = self.client.get(reverse('recommendations:item_list', args=[self.category_1.pk]), {'search': '1'})

        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['object_list'], [self.item_1], ordered=False)

    def test_item_list_view_not_authenticated_without_query(self):
        response = self.client.get(reverse('recommendations:item_list', args=[self.category_1.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['object_list'], [self.item_1, self.item_2], ordered=False)

    def test_item_detail_view(self):
        response = self.client.get(reverse('recommendations:item_detail', args=[self.item_1.pk]))
        self.assertEqual(response.status_code, 200)

    def test_item_detail_view_not_published(self):
        self.item_1.is_published = False
        self.item_1.save()
        self.client.force_login(self.user)
        response = self.client.get(reverse('recommendations:item_detail', args=[self.item_1.pk]))
        self.assertEqual(response.status_code, 403)

    def test_item_create_view_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('recommendations:item_create'), {
            'name': "New Item",
            'description': "New Description",
            'is_published': True,
            'category': self.category_1.pk
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Item.objects.filter(name="New Item").exists())

    def test_item_update_view_authenticated_and_owner(self):
        self.client.force_login(self.user_owner)
        response = self.client.post(reverse('recommendations:item_update', args=[self.item_1.pk]), {
            'name': "Updated Item",
            'description': "Updated Description"
        })
        self.item_1.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.item_1.name, "Updated Item")

    def test_item_update_view_authenticated_not_owner(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('recommendations:item_update', args=[self.item_1.pk]), {
            'name': "Attempted Update",
            'description': "Should not change",
            'is_published': True,
            'category': self.category_1.pk
        })
        self.assertEqual(response.status_code, 403)

    def test_item_delete_view_authenticated_and_owner(self):
        self.client.force_login(self.user_owner)
        response = self.client.post(reverse('recommendations:item_delete', args=[self.item_1.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Item.objects.filter(pk=self.item_1.pk).exists())

    def test_item_delete_view_authenticated_not_owner(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('recommendations:item_delete', args=[self.item_1.pk]))
        self.assertEqual(response.status_code, 403)

    def test_recommended_items_view(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('recommendations:item_recommended'))

        self.assertEqual(response.status_code, 200)

    def test_statistic_view(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('recommendations:statistic'))

        self.assertEqual(response.status_code, 200)

    def test_get_contacts_post(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('recommendations:contacts'), {
            'email': 'test@test.com',
            'message': 'This is a test message.'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)

    def test_get_contacts_post_invalid(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('recommendations:contacts'), {
            'email': '',
            'message': 'This should not work.'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)

    def test_get_contacts_get(self):
        response = self.client.get(reverse('recommendations:contacts'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recommendations/contacts.html')
        self.assertIn('form', response.context)


class LikeTestCase(TestCase):
    """Класс тестирования контроллеров модели Like"""

    def setUp(self):
        self.user_owner = User.objects.create(email='user_owner@test.com', password='password', phone="88005553535")
        self.user = User.objects.create(email='user@test.com', password='password', phone="88005553535")

        self.category_1 = Category.objects.create(name="test1", description="test")

        zone = pytz.timezone(settings.TIME_ZONE)
        self.now = datetime.now(zone)

        self.item_1 = Item.objects.create(
            name="test1",
            description="test",
            created_at=self.now,
            is_published=True,
            user=self.user_owner,
            category=self.category_1
        )
        self.item_2 = Item.objects.create(
            name="test2",
            description="test",
            created_at=self.now,
            is_published=True,
            user=self.user_owner,
            category=self.category_1
        )

        self.like_1 = Like.objects.create(user=self.user, item=self.item_1)

    def test_user_like_list_view(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('recommendations:user_like_list'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['object_list'],
            [self.item_1],
            ordered=False
        )

    def test_user_like_list_view_no_likes(self):
        self.client.logout()
        new_user = User.objects.create(email='new_user@test.com', password='password', phone="88005553535")
        self.client.force_login(new_user)
        response = self.client.get(reverse('recommendations:user_like_list'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['object_list'], [], ordered=False)

    def test_like_item_authenticated(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse('recommendations:item_like', args=[self.item_2.pk]))
        self.item_2.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.item_2.count_likes, 1)

    def test_like_item_already_liked(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('recommendations:item_like', args=[self.item_1.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.item_1.count_likes, 0)

    def test_like_item_by_owner(self):
        self.client.force_login(self.user_owner)
        response = self.client.post(reverse('recommendations:item_like', args=[self.item_1.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.item_1.count_likes, 0)

    def test_like_item_not_published(self):
        self.item_2.is_published = False
        self.item_2.save()
        self.client.force_login(self.user)
        response = self.client.post(reverse('recommendations:item_like', args=[self.item_2.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.item_2.count_likes, 0)

    def test_unlike_item_authenticated(self):
        self.client.force_login(self.user)
        Like.objects.create(user=self.user, item=self.item_2)
        response = self.client.post(reverse('recommendations:item_unlike', args=[self.item_2.pk]))
        self.item_2.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.item_2.count_likes, -1)

    def test_unlike_item_not_liked(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('recommendations:item_unlike', args=[self.item_2.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.item_2.count_likes, 0)

    def test_unlike_item_not_authenticated(self):
        response = self.client.post(reverse('recommendations:item_unlike', args=[self.item_1.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.item_1.count_likes, 0)


class CollaborativeFilteringTestCase(TestCase):
    """Класс тестирования алгоритмов PageRank, коллаборативной фильтрации и kNN"""

    def setUp(self):
        self.user_1 = User.objects.create(email='user_1@test.com', password='password', phone="88005553535")
        self.user_2 = User.objects.create(email='user_2@test.com', password='password', phone="88005553535")
        self.user_3 = User.objects.create(email='user_3@test.com', password='password', phone="88005553535")

        self.item_1 = Item.objects.create(
            name="test_1",
            description="test"
        )
        self.item_2 = Item.objects.create(
            name="test_2",
            description="test"
        )
        self.item_3 = Item.objects.create(
            name="test_3",
            description="test"
        )

        Like.objects.create(user=self.user_1, item=self.item_1)
        Like.objects.create(user=self.user_1, item=self.item_2)
        Like.objects.create(user=self.user_2, item=self.item_2)
        Like.objects.create(user=self.user_2, item=self.item_3)
        Like.objects.create(user=self.user_3, item=self.item_1)

    def test_create_likes_graph(self):
        graph = create_likes_graph()

        self.assertEqual(len(graph.nodes), 6)

        self.assertIn((self.user_1.email, self.item_1.pk), graph.edges)
        self.assertIn((self.user_1.email, self.item_2.pk), graph.edges)
        self.assertIn((self.user_2.email, self.item_2.pk), graph.edges)
        self.assertIn((self.user_2.email, self.item_3.pk), graph.edges)
        self.assertIn((self.user_3.email, self.item_1.pk), graph.edges)

    def test_page_rank_alg(self):
        graph = create_likes_graph()
        nodes = [self.user_1.email, self.user_2.email, self.user_3.email]

        popularity = page_rank_alg(graph, nodes)

        self.assertGreater(len(popularity), 0)
        for node in nodes:
            self.assertIn(node, popularity)

    def test_knn_alg(self):
        graph = create_likes_graph()
        current_user_items = list(graph.neighbors(self.user_1.email))
        k = 2

        same_interest_users = kNN_alg(graph, self.user_1.email, current_user_items, k)

        self.assertGreater(len(same_interest_users), 0)
        for user in same_interest_users:
            self.assertTrue(User.objects.filter(email=user).exists())

    def test_get_same_interest_users(self):
        k = 2
        graph, current_user_items, same_interest_users = get_same_interest_users(self.user_1.email, k)

        self.assertIsInstance(graph, nx.Graph)
        self.assertGreater(len(current_user_items), 0)
        self.assertGreater(len(same_interest_users), 0)

    def test_collaborative_filtering(self):
        recommended_items_ids = collaborative_filtering_alg(self.user_1.email)
        recommended_items = Item.objects.filter(pk__in=recommended_items_ids)

        self.assertNotIn(self.item_1, recommended_items)
        self.assertNotIn(self.item_2, recommended_items)
        self.assertIn(self.item_3, recommended_items)
        self.assertGreater(len(recommended_items), 0)

    def test_get_statistics(self):
        self.item_1.count_likes = 2
        self.item_1.save()

        self.item_2.count_likes = 2
        self.item_2.save()

        self.item_3.count_likes = 1
        self.item_3.save()

        same_interest_users, most_popular_items = get_statistics(self.user_1.email)

        self.assertGreater(len(same_interest_users), 0)
        self.assertIn(self.user_2.email, same_interest_users)
        self.assertIn(self.user_3.email, same_interest_users)

        self.assertEqual(most_popular_items.count(), 3)

    def test_user_likes_count(self):
        user_likes_count = Like.objects.filter(user=self.user_1).count()
        self.assertEqual(user_likes_count, 2)

    def test_item_like_count(self):
        item1_likes_count = Like.objects.filter(item=self.item_1).count()
        self.assertEqual(item1_likes_count, 2)
