from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post
from .settings import POSTS_ON_PAGE, POSTS_ON_PROFILE_PAGE

User = get_user_model()


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
    form = PostForm(request.POST or None)
    if not form.is_valid():
        return render(request, "new.html", {"form": form,
                                            "html_title": 'Добавить запись',
                                            'submit': 'Добавить'})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect("index")


def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user)
    posts_count = Post.objects.filter(author=user).count()
    paginator = Paginator(posts, POSTS_ON_PROFILE_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'profile.html', {'username': user,
                                            'posts_count': posts_count,
                                            'page': page})


def post_view(request, username, post_id):
    # тут тело функции
    post = Post.objects.get(id=post_id)
    author = post.author
    return render(request, 'post.html', {'post': post, 'author': author})


@login_required
def post_edit(request, username, post_id):
    if username != request.user.username:
        return redirect('post', username=username, post_id=post_id)
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    form = PostForm(instance=post, data=request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('post', username=username, post_id=post_id)
    return render(request, 'new.html', {'form': form,
                                        'html_title': 'Редактировать запись',
                                        'submit': 'Сохранить'})
