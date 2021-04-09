import datetime as dt
import itertools

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
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
        self.guest_client = Client()
        self.user = User.objects.create_user(username='IvanovI')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        slug = self.group.slug
        self.url_names = {
            'index.html': reverse('index'),
            'group.html': reverse('group_posts', kwargs={'slug': slug}),
            'new.html': reverse('new_post')
        }

        self.test_post = {
            'text': "Ж" * 50,
            'pub_date': self.post.pub_date,
            'author': 'test_user',
            'group': 'Тест-название',
            'slug': slug
        }

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for template, reverse_name in self.url_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_main_page_shows_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('index'))
        first_object = response.context['page'][0]
        dictionary = {
            'text': first_object.text,
            'pub_date': first_object.pub_date,
            'author': first_object.author.username,
            'group': first_object.group.title,
        }
        for key, value in itertools.islice(self.test_post.items(), 3):
            with self.subTest(value=value):
                self.assertEqual(dictionary[key], value)

    def test_group_page_shows_correct_context(self):
        """Шаблон группы сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('group_posts',
                                                 kwargs={'slug':
                                                         self.group.slug}))
        first_object = response.context['page'][0]
        dictionary = {
            'text': first_object.text,
            'pub_date': first_object.pub_date,
            'author': first_object.author.username,
            'group': first_object.group.title,
            'slug': first_object.group.slug,
        }
        for key, value in itertools.islice(self.test_post.items(), 4):
            with self.subTest(value=value):
                self.assertEqual(dictionary[key], value)

    def test_new_post_page_shows_correct_context(self):
        """Шаблон home сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_on_relevant_page(self):
        '''Пост отображается на главной странице и странице группы'''
        form_data = {
            'group': Group.objects.create(title='т_группа', slug='t_group').id,
            'text': 'тестовая публикация',
            'author': self.user,
            'pub_date': dt.datetime.today().date()
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        with self.subTest():
            self.assertRedirects(response, reverse('index'))

        with self.subTest():
            response = self.authorized_client.get(reverse('index'))
            context = response.context['page'][0]
            self.assertEqual(context.text, form_data['text'])

        # Отображение на странице выбранной группы
        response1 = self.authorized_client.get(reverse('group_posts',
                                                       kwargs={'slug':
                                                               't_group'})
                                               )
        response2 = self.authorized_client.get(self.url_names['group.html'])
        context_group1 = response1.context['page'][0]
        context_group2 = response2.context['page'][0]
        with self.subTest():
            self.assertEqual(context_group1.text, form_data['text'])
            self.assertNotEqual(context_group2.text, form_data['text'])

# дописать текст для Paginator для index и group_posts =>


# Здесь импорт необходимых библиотек для тестов.


class PaginatorViewsTest(TestCase):
    # Здесь создаются фикстуры: клиент и 13 тестовых записей.
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
        for i in range(0, 12):
            Post.objects.create(text="Ж" * i,
                                group=cls.group,
                                author=author,
                                pub_date=pub_date)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='IvanovI')

    def test_first_page_containse_ten_records(self):
        response = self.client.get(reverse('index'))
        # Проверка: количество постов на первой странице равно 10.

        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_second_page_containse_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.client.get(reverse('index') + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 3)
