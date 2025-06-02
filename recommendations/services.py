import networkx as nx
import pytz
from django.core.cache import cache

from config import settings
from datetime import datetime
from recommendations.models import Like, Item, Category

ZONE = pytz.timezone(settings.TIME_ZONE)
NOW = datetime.now(ZONE)


def create_likes_graph():
    """Функция построения графа с соотношением пользователей и элементов системы"""

    G = nx.Graph()

    likes = Like.objects.all()

    for like in likes:
        G.add_node(like.user.email, type='user')
        G.add_node(like.item.pk, type='item')
        G.add_edge(like.user.email, like.item.pk)

    return G


def page_rank_alg(graph, current_user_items, same_interest_users):
    """Функция реализации алгоритма PageRank для расчета важности пользователей"""

    same_users_popularity = {}
    current_user_items = set(current_user_items)

    for same_user in same_interest_users:
        same_user_items = set(graph.neighbors(same_user))
        weight = len(current_user_items & same_user_items)
        same_users_popularity[same_user] = weight

    return same_users_popularity


def kNN_alg(graph, user_email, current_user_items, k):
    """Функция реализации алгоритма k-Nearest Neighbors для нахождения k-ближайших пользователей"""

    same_interest_users = []
    for item in current_user_items:
        item_users = list(graph.neighbors(item))
        item_users.remove(user_email)
        same_interest_users.extend(item_users)

    same_users_popularity = page_rank_alg(graph, current_user_items, list(set(same_interest_users)))

    most_same_interest_users = sorted(same_users_popularity, key=same_users_popularity.get, reverse=True)

    return most_same_interest_users[:k]


def get_same_interest_users(user_email, k):
    """Функция получения пользователей с похожими интересами"""

    graph = create_likes_graph()
    current_user_items = list(graph.neighbors(user_email))

    same_interest_users = kNN_alg(graph, user_email, current_user_items, k)

    return graph, current_user_items, same_interest_users


def collaborative_filtering_alg(user_email, k=5):
    """Функция реализации алгоритма коллаборативной фильтрации для расчета рекомендаций пользователю"""

    graph, current_user_items, same_interest_users = get_same_interest_users(user_email, k)

    recommended_items = []
    for user in same_interest_users:
        user_items = graph.neighbors(user)
        user_items = list(set(user_items) - set(current_user_items))
        recommended_items.extend(user_items)

    return list(set(recommended_items))


def get_statistics(user_email, k=10, count_items=10):
    """Функция для получения статистики"""

    _, _, same_interest_users = get_same_interest_users(user_email, k)

    if settings.CACHE_ENABLED:
        key = f'most_popular_items_{user_email}'
        most_popular_items = cache.get(key)

        if most_popular_items is None:
            most_popular_items = Item.objects.filter(count_likes__gt=0).order_by('-count_likes')[:count_items]
            cache.set(key, most_popular_items)
    else:
        most_popular_items = Item.objects.filter(count_likes__gt=0).order_by('-count_likes')[:count_items]

    return same_interest_users, most_popular_items


def cache_category_list():
    """Функция кеширования списка объектов модели Category"""

    if settings.CACHE_ENABLED:
        key = 'category_list'
        category_list = cache.get(key)

        if category_list is None:
            category_list = Category.objects.all()
            cache.set(key, category_list)
    else:
        category_list = Category.objects.all()

    return category_list


def cache_item_list(category_published_items, user=None):
    """Функция кеширования списка объектов модели Item"""

    if settings.CACHE_ENABLED:
        key = 'item_list'
        item_list = cache.get(key)

        if item_list is None:
            if user is not None:
                item_list = category_published_items.exclude(user=user).order_by('?')
            else:
                item_list = category_published_items.order_by('?')
            cache.set(key, item_list)

    else:
        if user is not None:
            item_list = category_published_items.exclude(user=user).order_by('?')
        else:
            item_list = category_published_items.order_by('?')

    return item_list
