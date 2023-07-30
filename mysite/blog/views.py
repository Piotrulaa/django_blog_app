from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail
from django.conf import settings
from taggit.models import Tag
from django.db.models import Count
from django.http import HttpResponse, HttpRequest

from .forms import EmailPostForm, CommentForm
from .models import Post, Comment


def post_list(request: HttpRequest, tag_slug: str = None) -> HttpResponse:
    object_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])
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
            "posts": posts,
            "tag": tag,
        }
    )


def post_share(request: HttpRequest, post_id: int) -> HttpResponse:
    post = get_object_or_404(Post, id=post_id, status="published")
    sent = False
    if request.method == "POST":
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = "{} ({}) zachęca do przeczytania \"{}\"".format(
                cd["name"], cd["email"], post.title
            )
            message = "Przeczytaj post \"{}\" na stronie {}\n\nKomentarz dodany przez {}: {}".format(
                post.title, post_url, cd["name"], cd["comments"]
            )
            send_mail(subject, message, settings.EMAIL_SENDER_ADDRESS, [cd["to"]])
            sent = True
    else:
        # If request method is not POST, return empty form
        form = EmailPostForm()
    return render(
        request,
        template_name="blog/post/share.html",
        context={
            "post": post,
            "form": form,
            "sent": sent,
        }
    )


def post_detail(request: HttpRequest, year: int, month: int, day: int, post: str) -> HttpResponse:
    post = get_object_or_404(
        Post,
        slug=post,
        publish__year=year,
        publish__month=month,
        publish__day=day
    )
    comments = post.comments.filter(active=True)
    new_comment = None
    if request.method == "POST":
        # Comments has been added
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
    else:
        comment_form = CommentForm()
    # Retrieving similar posts
    max_count = 4
    post_tags_ids = post.tags.values_list("id", flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count("tags")).order_by("-same_tags", "-publish")[:max_count]
    return render(
        request,
        template_name="blog/post/detail.html",
        context={
            "post": post,
            "comments": comments,
            "comment_form": comment_form,
            "new_comment": new_comment,
            "similar_posts": similar_posts,
        }
    )
