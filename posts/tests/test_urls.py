import datetime as dt
import itertools

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(title="Тест-название",
                                         slug='test_slug',
                                         description="Тест-описание")
        pub_date = dt.datetime.now().date()
        author = User.objects.create_user(username='test_user')
        cls.post = Post.objects.create(text="Ж" * 50,
                                       group=cls.group,
                                       author=author,
                                       pub_date=pub_date)

    def setUp(self):
        # Создаём экземпляр клиента. Он неавторизован.
        self.guest_client = Client()
        # создаем пользователя
        self.user = User.objects.create_user(username='IvanovI')
        # создаем второй клиент
        self.authorized_client = Client()
        # авторизируем пользователя
        self.authorized_client.force_login(self.user)

        slug = self.group.slug
        self.url_names = {
            'index.html': reverse('index'),
            'group.html': reverse('group_posts', kwargs={'slug': slug}),
            'new.html': reverse('new_post')}
        self.clients = ['authorized_client', 'guest_client']

    # 1. Проверка запросов к страницам
    def test_unauth_user_url_exists(self):
        """Проверка доступности адресов любого клиента"""
        for template, url in itertools.islice(self.url_names.items(), 2):
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_auth_user_urls_exists(self):
        """Проверка доступности адресов для авторизированного клиента"""
        for template, url in itertools.islice(self.url_names.items(), 3):
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
        for template, url in itertools.islice(self.url_names.items(), 3):
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template, 'не найден шаблон '
                                                            f'{template} для '
                                                            f'страницы '
                                                            f'{url}')

    # 3. Проверка редиректов

# class UserLoginTests(TestCase):
#     def setUpClass(cls):
#         # создание неавторизированного клиента
#         cls.guest_client = Client()

#     def setUp(self):
#         self.superuser = User.objects.create_superuser(
#             email='info@ya.ru',
#             password='test_password',
#             username='Test_Super_User')
#         self.login = self.client.login(username='Test_Super_User',
#                                        password='test_password')
#         self.resp = self.client.get('/new')

#     def test_login(self):
#         """проверка того, что пользователь залогинен"""
#         self.assertTrue(self.login)

#     def test_registered_user_url_uses_correct_template(self):
#         self.assertTrue(self.resp)
