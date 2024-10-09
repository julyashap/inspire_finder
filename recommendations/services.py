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
        G.add_node(like.user.email, type='user')
        G.add_node(like.item.pk, type='item')
        G.add_edge(like.user.email, like.item.pk)

    return G


def page_rank_alg(graph, nodes):
    """Функция реализации алгоритма PageRank для расчета важности узлов"""

    nodes_popularity = {}
    for node in nodes:
        nodes_popularity[node] = graph.degree(node) * 0.1

    nodes_popularity = sorted(nodes_popularity.keys(), key=nodes_popularity.get)

    return nodes_popularity


def kNN_alg(graph, user_email, current_user_items, k):
    """Функция реализации алгоритма k-Nearest Neighbors для нахождения k-ближайших пользователей"""

    same_interest_users = []
    for item in current_user_items:
        item_users = list(graph.neighbors(item))
        item_users.remove(user_email)
        same_interest_users.extend(item_users)

    return list(set(same_interest_users))[:k]


def get_same_interest_users(user_email, k):
    graph = create_likes_graph()
    current_user_items = list(graph.neighbors(user_email))

    same_interest_users = kNN_alg(graph, user_email, current_user_items, k)

    return graph, current_user_items, same_interest_users


def collaborative_filtering_alg(user_email, k=5):
    """Функция реализации алгоритма коллаборативной фильтрации для расчета рекомендаций пользователю"""

    graph, current_user_items, same_interest_users = get_same_interest_users(user_email, k)

    recommended_items = []
    for user in same_interest_users:
        user_items = list(graph.neighbors(user))
        user_items = list(set(user_items) - set(current_user_items))
        recommended_items.extend(user_items)

    return list(set(recommended_items))


def get_statistics(user_email, k=10, count_items=10):
    graph, _, same_interest_users = get_same_interest_users(user_email, k)

    items = [node for node, attrs in graph.nodes(data=True) if attrs.get('type') == 'item']
    most_popular_items = page_rank_alg(graph, items)[:count_items]

    return same_interest_users, most_popular_items
