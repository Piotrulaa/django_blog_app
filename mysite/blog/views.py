from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Post


def post_list(request):
    object_list = Post.published.all()
    paginator = Paginator(object_list, 3)  # 3 posts per page
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not int, return first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is greater than total number of pages, return last page
        posts = paginator.page(paginator.num_pages)
    return render(
        request,
        template_name="blog/post/list.html",
        context={
            "page": page,
            "posts": posts
        }
    )


def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post,
        slug=post,
        publish__year=year,
        publish__month=month,
        publish__day=day
    )
    return render(
        request,
        template_name="blog/post/detail.html",
        context={"post": post}
    )
