from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User
from posts.settings import POSTS_ON_PAGE

HOME_PAGE, NEW_POST = reverse('index'), reverse('new_post')

POST_TEST_TEXT = "Ж" * 50


class PostPagesTests(TestCase):
    def setUp(self):
        self.group = Group.objects.create(title="Тест-название",
                                          slug='test_slug',
                                          description="Тест-описание")

        # первый клиент автор поста
        self.GUEST_CLIENT = Client()
        self.USER = User.objects.create_user(username='IvanovI')
        self.AUTHORIZED_CLIENT = Client()
        self.AUTHORIZED_CLIENT.force_login(self.USER)
        self.USERNAME = self.USER.username
        # второй клиент не автор поста
        self.AUTHORIZED_CLIENT_2 = Client()
        self.user_2 = User.objects.create_user(username='PetrovP')
        self.AUTHORIZED_CLIENT_2 = Client()
        self.AUTHORIZED_CLIENT_2.force_login(self.user_2)
        self.username_2 = self.user_2.username

        # создание поста
        self.post = Post.objects.create(text=POST_TEST_TEXT,
                                        group=self.group,
                                        author=self.USER)
        # библиотека юрлов
        self.POST_ID = self.post.id
        self.SLUG = self.group.slug
        self.GROUP_PAGE = reverse('group_posts', kwargs={'slug': self.SLUG})
        self.PROFILE_PAGE = reverse('profile', kwargs={'username':
                                                       self.USERNAME})
        self.POST_PAGE = reverse('post', kwargs={'username':
                                                 self.USERNAME,
                                                 'post_id': self.POST_ID})
        self.EDIT_PAGE = reverse('post_edit',
                                 kwargs={'username': self.USERNAME,
                                         'post_id': self.post.id, })

    # Проверяем контекст
    def test_main_group_pages_shows_correct_context(self):
        """Страница index, group сформированы с правильным контекстом."""
        urls = [['index.html', HOME_PAGE],
                ['group.html', self.GROUP_PAGE], ]

        for template, url in urls:
            with self.subTest(url=url):
                response = self.GUEST_CLIENT.get(url)
                first_object = response.context['page'][0]
                field_values = [[POST_TEST_TEXT, first_object.text],
                                [self.USERNAME, first_object.author.username],
                                [self.group.title, first_object.group.title], ]

                for field, value in field_values:
                    self.assertEqual(field, value)

    def test_slug_pages_shows_correct_context(self):
        """Страница profile и post сформированы с правильным контекстом."""

        urls = [self.PROFILE_PAGE, self.POST_PAGE, ]
        response = self.GUEST_CLIENT.get(urls[0])
        first_object = response.context['page'][0]
        field_values = [[POST_TEST_TEXT, first_object.text],
                        [self.USERNAME, first_object.author.username],
                        [self.group.title, first_object.group.title], ]
        self.assertEqual(Post.objects.count(), 1)
        for field, value in field_values:
            with self.subTest(value=value):
                self.assertEqual(field, value, f'{field} {value}')

        response = self.GUEST_CLIENT.get(urls[1])
        first_object = response.context['post']
        field_values = [[POST_TEST_TEXT, first_object.text],
                        [self.USERNAME, first_object.author.username],
                        [self.group.title, first_object.group.title], ]
        self.assertEqual(Post.objects.count(), 1)
        for field, value in field_values:
            with self.subTest(value=value):
                self.assertEqual(field, value, f'{field} {value}')

    def test_post_on_relevant_page(self):
        '''Пост отображается на главной странице и странице группы'''
        form_data = {
            'group': Group.objects.create(title='т_группа', slug='t_group'),
            'text': 'тестовая публикация',
            'author': self.USER
        }

        Post.objects.create(text=form_data['text'],
                            group=form_data['group'],
                            author=self.USER)

        with self.subTest():
            response = self.GUEST_CLIENT.get(HOME_PAGE)
            context = response.context['page'][0]
            self.assertEqual(context.text, form_data['text'])

        # Отображение на странице выбранной группы
        response1 = self.AUTHORIZED_CLIENT.get(reverse('group_posts',
                                               kwargs={'slug':
                                                       't_group'}))
        response2 = self.AUTHORIZED_CLIENT.get(self.GROUP_PAGE)
        context_group1 = response1.context['page'][0]
        context_group2 = response2.context['page'][0]
        with self.subTest():
            self.assertEqual(context_group1.text, form_data['text'])
            self.assertNotEqual(context_group2.text, form_data['text'])

    def test_post_edit_by_author(self):
        '''Автор поста может редактировать свой пост
        и производит обновление базы данных'''
        posts_count_before = Post.objects.count()
        form_data = {
            'group': self.group.id,
            'text': 'тестовая публикация'
        }
        self.AUTHORIZED_CLIENT.post(self.EDIT_PAGE,
                                    data=form_data, follow=True)
        # print(response.context)  #print(response.context)
        edited_post = Post.objects.get(pk=self.post.id)
        self.assertEqual(edited_post.text, 'тестовая публикация')
        self.assertEqual(posts_count_before, Post.objects.count())


class PaginatorViewsTest(TestCase):
    def setUp(self):

        self.group = Group.objects.create(title="Тест-название",
                                          slug='test_slug',
                                          description="Тест-описание")
        author = User.objects.create_user(username='test_user')

        for i in range(0, 13):
            Post.objects.create(text="Ж" * i,
                                group=self.group,
                                author=author)
        slug = self.group.slug
        self.GUEST_CLIENT = Client()
        self.USER = User.objects.create_user(username='IvanovI')
        self.GROUP_PAGE = reverse('group_posts', kwargs={'slug':
                                                         slug})
        self.url_names = {
            'index.html': HOME_PAGE,
            'group.html': self.GROUP_PAGE,
            'new.html': NEW_POST
        }

    def test_first_page_containse_ten_records(self):
        '''На 1,2 стр Paginator отображается нужное количество записей'''
        posts_count = Post.objects.count()
        second_page_posts_count = posts_count - POSTS_ON_PAGE
        urls = [[HOME_PAGE, POSTS_ON_PAGE],
                [self.GROUP_PAGE, POSTS_ON_PAGE],
                [HOME_PAGE + '?page=2', second_page_posts_count],
                [self.GROUP_PAGE + '?page=2', second_page_posts_count], ]

        for url, length in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                len_list = len(response.context.get('page').object_list)
                self.assertEqual(len_list, length)
