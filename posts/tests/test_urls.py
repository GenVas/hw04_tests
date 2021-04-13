from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

HOME_PAGE, NEW_POST = reverse('index'), reverse('new_post')


class StaticURLTests(TestCase):
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
        self.USERNAME_2 = self.user_2.username
        # создание поста
        self.post = Post.objects.create(text="Ж" * 50,
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

    # 1. Проверка запросов к страницам
    def test_url_exists(self):
        """Проверка доступности адресов любого клиента"""

        url_names = [[HOME_PAGE, self.GUEST_CLIENT, 200],
                     [HOME_PAGE, self.AUTHORIZED_CLIENT, 200],
                     [self.GROUP_PAGE, self.GUEST_CLIENT, 200],
                     [self.GROUP_PAGE, self.AUTHORIZED_CLIENT, 200],
                     [self.POST_PAGE, self.GUEST_CLIENT, 200],
                     [self.POST_PAGE, self.AUTHORIZED_CLIENT, 200],
                     [self.PROFILE_PAGE, self.GUEST_CLIENT, 200],
                     [self.PROFILE_PAGE, self.AUTHORIZED_CLIENT, 200],
                     [NEW_POST, self.GUEST_CLIENT, 302],
                     [NEW_POST, self.AUTHORIZED_CLIENT, 200],
                     [self.EDIT_PAGE, self.GUEST_CLIENT, 302],
                     [self.EDIT_PAGE, self.AUTHORIZED_CLIENT, 200],
                     [self.EDIT_PAGE, self.AUTHORIZED_CLIENT_2, 302], ]

        for stack in url_names:
            with self.subTest(stack=stack):
                response = stack[1].get(stack[0])
                self.assertEqual(response.status_code, stack[2])

    # 2. Проверка шаблонов
    def test_unauth_user_url_uses_correct_templates(self):
        """Проверка шаблона '/' """
        templates = ['index.html', 'index.html', 'group.html', 'group.html',
                     'post.html', 'post.html', 'profile.html', 'profile.html',
                     'new.html', 'new.html', 'post.html',
                     'post.html', 'post.html']
        url_names = []
        for i in url_names:
            for i in templates:
                url_names[3] = templates[i]

        for stack in url_names:
            with self.subTest(stack=stack):
                response = stack[1].get(stack[0])
                self.assertTemplateUsed(response, stack[3], 'не найден шаблон '
                                                            f'{stack[3]} для '
                                                            f'страницы '
                                                            f'{stack[0]}')

    # Проверка редиректов
    def test_post_edit_redirect(self):
        """Со странцы редактирования не автор направлен на страницу поста."""
        form_data = {
            'group': self.group.id,
            'text': 'тестовая публикация'}

        self.AUTHORIZED_CLIENT_2.post(self.EDIT_PAGE,
                                      data=form_data, follow=True)

        response = self.AUTHORIZED_CLIENT_2.post(self.EDIT_PAGE,
                                                 data=form_data, follow=True)
        self.assertRedirects(response, self.POST_PAGE)
