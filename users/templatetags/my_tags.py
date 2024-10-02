from django import template
from config.settings import MEDIA_URL
import os.path

register = template.Library()


@register.filter()
def media_path(path):
    if path:
        return os.path.join(MEDIA_URL, str(path))
    return "#"
