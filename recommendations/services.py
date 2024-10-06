import networkx as nx
import pytz
from config import settings
from datetime import datetime
from recommendations.models import Like

ZONE = pytz.timezone(settings.TIME_ZONE)
NOW = datetime.now(ZONE)


def create_likes_graph():
    """Функция построения графа с соотношением пользователей и элементов системы"""

    G = nx.Graph()

    likes = Like.objects.all()

    for like in likes:
        G.add_node(like.user.pk, type='user')
        G.add_node(like.item.pk, type='item')
        G.add_edge(like.user.pk, like.item.pk)

    return G


def page_rank_alg(graph, nodes):
    """Функция реализации алгоритма PageRank для расчета важности узлов"""

    nodes_popularity = {}
    for node in nodes:
        nodes_popularity[node] = graph.degree(node) * 0.1

    nodes_popularity = sorted(nodes_popularity.keys(), key=nodes_popularity.get)

    return nodes_popularity


def kNN_alg(graph, user_pk, current_user_items, k):
    """Функция реализации алгоритма k-Nearest Neighbors для нахождения k-ближайших пользователей"""

    same_interest_users = []
    for item in current_user_items:
        item_users = list(graph.neighbors(item))
        item_users.remove(user_pk)
        same_interest_users.extend(item_users)

    return list(set(same_interest_users))[:k]


def collaborative_filtering_alg(user_pk, k=3):
    """Функция реализации алгоритма коллаборативной фильтрации для расчета рекомендаций пользователю"""

    graph = create_likes_graph()
    current_user_items = list(graph.neighbors(user_pk))

    same_interest_users = kNN_alg(graph, user_pk, current_user_items, k)

    recommended_items = []
    for user in same_interest_users:
        user_items = list(graph.neighbors(user))
        user_items = list(set(user_items) - set(current_user_items))
        recommended_items.extend(user_items)

    return list(set(recommended_items))
