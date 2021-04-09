from django.urls import path

from . import views

urlpatterns = [
    path('author/', views.AboutAuthorStaticPage.as_view(), name='author'),
    path('tech/', views.AboutAuthorStaticPage.as_view(), name='tech'),
]
