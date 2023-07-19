from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords

from .models import Post


class LatestPostFeed(Feed):
    title = "Mój blog"
    link = "/blog/"
    description = "Nowe posty na moim blogu"

    def items(self):
        items_count = 5
        return Post.published.all()[:items_count]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        words_count = 30
        return truncatewords(item.body, words_count)
