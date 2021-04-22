from django.urls import path

from . import views

urlpatterns = [
    path("404/", views.page_not_found),
    path("500/", views.server_error),
    path('new/', views.new_post, name="new_post"),
    path('group/<slug:slug>/', views.group_posts,
         name="group_posts"),
    path('<str:username>/', views.profile, name='profile'),
    # Просмотр записи
    path('<str:username>/<int:post_id>/edit/',
         views.post_edit, name='post_edit'),
    # Профайл пользователя
    path('<str:username>/<int:post_id>/', views.post_view,
         name='post'),
    path('<username>/<int:post_id>/comment/', views.add_comment, name="add_comment"),
    path("", views.index, name="index"),
]
