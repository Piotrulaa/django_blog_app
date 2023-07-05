from django import template
from django.db.models import Count, Q

from ..models import Post


register = template.Library()

@register.simple_tag
def total_posts():
    return Post.published.count()

@register.inclusion_tag(filename="blog/post/latest_posts.html")
def show_latest_posts(count=5):
    latest_posts = Post.published.order_by("-publish")[:count]
    return {"latest_posts": latest_posts}

@register.simple_tag
def get_most_commented_posts(count=5):
    return Post.published.annotate(
        total_comments=Count("comments", filter=Q(comments__active=True))
    ).order_by("-total_comments").filter(total_comments__gt=0)[:count]
