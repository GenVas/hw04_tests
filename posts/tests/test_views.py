import datetime as dt
import itertools as it

from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class PostPagesTests(TestCase):
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
        # тестовый пост для проверки
        self.test_post = {
            'text': "Ж" * 50,
            'pub_date': self.post.pub_date,
            'author': self.username,
            'group': self.group.title,
            'slug': slug
        }

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for template, reverse_name in self.url_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    # Проверяем контекст
    def test_all_page_shows_correct_context(self):  # компилирую компактн верс
        """Шаблоны index, group, new сформированы с правильным контекстом."""
        for template, url in it.islice(self.url_names.items(), 2):
            with self.subTest(value=url):
                response = self.guest_client.get((url))
                first_object = response.context['page'][0]
                dictionary = {'text': first_object.text,
                              'pub_date': first_object.pub_date,
                              'author': first_object.author.username,
                              'group': first_object.group.title,
                              'slug': first_object.group.slug, }
                for key, value in it.islice(self.test_post.items(), 4):
                    self.assertEqual(dictionary[key], value)

    # Попробовал написать компактуню версию тестов, которые будут далее.
    # закомментил тесты для сравнения
    def test_all_page_shows_correct_context(self):
        """Шаблоны сформированы с правильным контекстом."""
        for template, url in it.islice(self.url_names.items(), 3, 4):
            with self.subTest(url=url):
                response = self.guest_client.get((url))
                first_object = response.context['page'][0]
                dictionary = {'text': first_object.text,
                              'pub_date': first_object.pub_date,
                              'author': first_object.author.username,
                              'group': first_object.group.title, }
                for key, value in it.islice(self.test_post.items(), 4):
                    self.assertEqual(dictionary[key], value)

    # def test_main_page_shows_correct_context(self):
    #     """Шаблон index сформирован с правильным контекстом."""
    #     response = self.guest_client.get(reverse('index'))
    #     first_object = response.context['page'][0]
    #     dictionary = {
    #         'text': first_object.text,
    #         'pub_date': first_object.pub_date,
    #         'author': first_object.author.username,
    #         'group': first_object.group.title,
    #     }
    #     for key, value in it.islice(self.test_post.items(), 3):
    #         with self.subTest(value=value):
    #             self.assertEqual(dictionary[key], value)

    # def test_group_page_shows_correct_context(self):
    #     """Шаблон группы сформирован с правильным контекстом."""
    #     response = self.guest_client.get(reverse('group_posts',
    #                                              kwargs={'slug':
    #                                                      self.group.slug}))
    #     first_object = response.context['page'][0]
    #     dictionary = {
    #         'text': first_object.text,
    #         'pub_date': first_object.pub_date,
    #         'author': first_object.author.username,
    #         'group': first_object.group.title,
    #     }
    #     for key, value in it.islice(self.test_post.items(), 4):
    #         with self.subTest(value=value):
    #             self.assertEqual(dictionary[key], value)

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
        response = self.authorized_client.post(reverse('new_post'),
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

    def test_post_edit_by_non_author(self):
        '''При редактировании поста не автором поста
        редактирование не осуществляется'''
        posts_count_before = Post.objects.count()
        form_data = {
            'group': self.group.id,
            'text': 'тестовая публикация'
        }
        self.authorized_client_2.post(reverse('post_edit',
                                              kwargs={'username':
                                                      self.username,
                                                      'post_id':
                                                      self.post.id, }),
                                      data=form_data, follow=True)
        edited_post = Post.objects.get(pk=self.post.id)
        self.assertNotEqual(edited_post.text, form_data['text'])
        self.assertEqual(posts_count_before, Post.objects.count())

    def test_post_edit_by_author(self):
        '''Автор поста может редактировать свой пост
        и происзодит обновление базы данных'''
        posts_count_before = Post.objects.count()
        form_data = {
            'group': self.group.id,
            'text': 'тестовая публикация'
        }
        self.authorized_client.post(reverse('post_edit',
                                    kwargs={'username': self.username,
                                            'post_id': self.post.id, }),
                                    data=form_data, follow=True)
        # print(response.context)  #print(response.context)
        edited_post = Post.objects.get(pk=self.post.id)
        self.assertEqual(edited_post.text, 'тестовая публикация')
        self.assertEqual(posts_count_before, Post.objects.count())

    def test_post_edit_by_guest(self):
        '''Гость не может редактировать пост'''
        posts_count_before = Post.objects.count()
        form_data = {
            'group': self.group.id,
            'text': 'тестовая публикация'
        }
        self.guest_client.post(reverse('post_edit',
                               kwargs={'username': self.username,
                                       'post_id': self.post.id, }),
                               data=form_data, follow=True)
        edited_post = Post.objects.get(pk=self.post.id)
        self.assertNotEqual(edited_post.text, form_data['text'])
        self.assertEqual(posts_count_before, Post.objects.count())


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(title="Тест-название",
                                         slug='test_slug',
                                         description="Тест-описание")
        pub_date = dt.datetime.now().date()
        author = User.objects.create_user(username='test_user')
        for i in range(0, 13):
            Post.objects.create(text="Ж" * i,
                                group=cls.group,
                                author=author,
                                pub_date=pub_date)

    def setUp(self):
        slug = self.group.slug
        self.guest_client = Client()
        self.user = User.objects.create_user(username='IvanovI')
        self.group_url = reverse('group_posts', kwargs={'slug':
                                                        slug})
        self.url_names = {
            'index.html': reverse('index'),
            'group.html': reverse('group_posts', kwargs={'slug': slug}),
            'new.html': reverse('new_post')
        }

    def test_first_page_containse_ten_records(self):
        '''На стр 1 Paginator отображает 10 записей'''
        for template, url in it.islice(self.url_names.items(), 1):
            with self.subTest(url=url):
                response = self.client.get(url)
                len_list = len(response.context.get('page').object_list)
                self.assertEqual(len_list, 10)

    def test_second_page_containse_three_records(self):
        '''На стр 2 Paginator отображает остальные записи'''
        for template, url in it.islice(self.url_names.items(), 1):
            with self.subTest(url=url):
                response = self.client.get(url + '?page=2')
                len_list = len(response.context.get('page').object_list)
                self.assertEqual(len_list, 3)
