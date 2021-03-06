from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import cache_page

from .forms import PostForm, CommentForm
from .models import Group, Post, User
from .settings import POSTS_ON_PAGE, POSTS_ON_PROFILE_PAGE

NEW_POST_SUBMIT_TITLE = _("Добавить запись")
NEW_POST_SUBMIT_BUTTON = _("Добавить")
EDIT_POST_SUBMIT_TITLE = _("Изменить запись")
EDIT_POST_SUBMIT_BUTTON = _("Сохранить")


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page, }
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "group.html", {"group": group, "page": page})


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if not form.is_valid():
        return render(request,
                      "new.html", {"form": form,
                                   "html_title": NEW_POST_SUBMIT_TITLE,
                                   "submit": NEW_POST_SUBMIT_BUTTON})
    post = form.save(commit=False)
    post.author = request.user
    form.save()
    return redirect("index")


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=author)
    paginator = Paginator(posts, POSTS_ON_PROFILE_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'profile.html', {'author': author,
                                            'page': page})


def post_view(request, username, post_id):
    post = Post.objects.get(id=post_id)
    author = post.author
    return render(request, 'post.html', {'post': post, 'author': author})


@login_required
def post_edit(request, username, post_id):
    if username != request.user.username:
        return redirect('post', username=username, post_id=post_id)
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    form = PostForm(instance=post,
                    data=request.POST or None,
                    files=request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('post', username=username, post_id=post_id)
    return render(request, 'new.html', {'form': form,
                                        'html_title': EDIT_POST_SUBMIT_TITLE,
                                        'submit': EDIT_POST_SUBMIT_BUTTON})


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    form = CommentForm(request.POST or None)
    if not form.is_valid():
        return render(request,
                      "comments.html", {"form": form})
    comment = form.save(commit=False)
    comment.author = request.user
    comment.post = post
    form.save()
    return redirect('post', username=username, post_id=post_id)


def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию,
    # выводить её в шаблон пользователской страницы 404 мы не станем
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)
