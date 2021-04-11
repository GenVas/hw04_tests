import datetime as dt
import itertools

from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(title="Тест-название",
                                         slug='test_slug',
                                         description="Тест-описание")

    def setUp(self):
        # первый клиент автор поста
        self.guest_client = Client()
        self.user = User.objects.create_user(username='IvanovI')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.username = self.user.username
        # второй клиент не автор поста
        self.authorized_client_2 = Client()
        self.user_2 = User.objects.create_user(username='PetrovP')
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.user_2)
        self.username_2 = self.user_2.username
        # создание поста
        pub_date = dt.datetime.now().date()
        self.post = Post.objects.create(text="Ж" * 50,
                                        group=self.group,
                                        author=self.user,
                                        pub_date=pub_date)
        # библиотека юрлов
        post_id = self.post.id
        slug = self.group.slug
        self.url_names = {
            'index.html': reverse('index'),
            'group.html': reverse('group_posts', kwargs={'slug': slug}),
            'new.html': reverse('new_post'),
            'profile.html': reverse('profile', kwargs={'username':
                                                       self.username}),
            'post.html': reverse('post', kwargs={'username':
                                                 self.username,
                                                 'post_id': post_id})
        }

    # 1. Проверка запросов к страницам
    def test_unauth_user_url_exists(self):
        """Проверка доступности адресов любого клиента"""
        for template, url in itertools.islice(self.url_names.items(), 2):
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_auth_user_urls_exists(self):
        """Проверка доступности адресов для авторизированного клиента"""
        for template, url in self.url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, 200)

    # 2. Проверка шаблонов
    def test_unauth_user_url_uses_correct_templates(self):
        """Проверка шаблона '/' """
        for template, url in itertools.islice(self.url_names.items(), 2):
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template, 'не найден шаблон '
                                                            f'{template} для '
                                                            f'страницы '
                                                            f'{url}')

    def test_auth_user_url_uses_correct_templates(self):
        """Проверка шаблонов для authorized_client"""
        for template, url in self.url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template, 'не найден шаблон '
                                                            f'{template} для '
                                                            f'страницы '
                                                            f'{url}')

    def test_auth_user_post_edit_url_uses_correct_templates(self):
        """Проверка шаблонов для authorized_client"""
        form_data = ['new.html', reverse('post_edit',
                                         kwargs={'username': self.username,
                                                 'post_id': self.post.id, })]
        response = self.authorized_client.get(form_data[1])
        self.assertTemplateUsed(response, form_data[0])

    # Проверка редиректов
    def test_post_edit_redirect(self):
        """Со странцы редактирования не автор направлен на страницу поста."""
        form_data = {
            'group': self.group.id,
            'text': 'тестовая публикация'}

        redirect_url = reverse('post', kwargs={'username': self.username,
                                               'post_id': self.post.id, })

        self.authorized_client_2.post(reverse('post_edit',
                                              kwargs={'username':
                                                      self.username,
                                                      'post_id':
                                                      self.post.id, }),
                                      data=form_data, follow=True)

        response = self.authorized_client_2.post(reverse('post_edit',
                                                 kwargs={'username':
                                                         self.username,
                                                         'post_id':
                                                         self.post.id}, ),
                                                 data=form_data, follow=True)
        self.assertRedirects(response, redirect_url)
