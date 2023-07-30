from django import template
from django.db.models import Count, Q
from django.utils.safestring import mark_safe
import markdown
from django.db.models.query import QuerySet
from django.utils.safestring import SafeString

from ..models import Post


register = template.Library()

@register.simple_tag
def total_posts() -> int:
    return Post.published.count()

@register.inclusion_tag(filename="blog/post/latest_posts.html")
def show_latest_posts(count: int = 5) -> dict[str, QuerySet]:
    latest_posts = Post.published.order_by("-publish")[:count]
    return {"latest_posts": latest_posts}

@register.simple_tag
def get_most_commented_posts(count: int = 5) -> QuerySet:
    return Post.published.annotate(
        total_comments=Count("comments", filter=Q(comments__active=True))
    ).order_by("-total_comments").filter(total_comments__gt=0)[:count]

@register.filter(name="markdown")
def markdown_format(text: str) -> SafeString:
    return mark_safe(markdown.markdown(text))
