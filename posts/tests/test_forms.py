from django import forms
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from posts.forms import PostForm
from posts.models import Group, Post, User

HOME_PAGE, NEW_POST = reverse('index'), reverse('new_post')
LABELS = {'group': _('Вы можете выбрать группу'),
          'text': _('Напишите сообщение')}
HELP_TEXTS = {'group': 'Поле не является обязательным',
              'text': _('Придумайте текст для поста. '
                        'Поле обязательно для заполнения'), }
POST_TEST_TEXT = "Ж" * 50


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(title="Тест-название",
                                         slug='test_slug',
                                         description="Тест-описание")
        cls.form = PostForm()

    def setUp(self):
        # первый клиент не автор поста
        self.GUEST_CLIENT = Client()
        self.USER = User.objects.create_user(username='IvanovI')
        self.AUTHORIZED_CLIENT = Client()
        self.AUTHORIZED_CLIENT.force_login(self.USER)
        self.USERNAME = self.USER.username
        self.authorized_client = Client()
        self.authorized_client.force_login(self.USER)

        # второй клиент не автор поста
        self.AUTHORIZED_CLIENT_2 = Client()
        self.user_2 = User.objects.create_user(username='PetrovP')
        self.AUTHORIZED_CLIENT_2 = Client()
        self.AUTHORIZED_CLIENT_2.force_login(self.user_2)
        self.username_2 = self.user_2.username

        slug = self.group.slug
        self.url_names = {
            'index.html': HOME_PAGE,
            'group.html': reverse('group_posts', kwargs={'slug': slug}),
            'new.html': NEW_POST}
        self.POST = Post.objects.create(text=POST_TEST_TEXT,
                                        group=self.group,
                                        author=self.USER)
        self.EDIT_PAGE = reverse('post_edit',
                                 kwargs={'username': self.USERNAME,
                                         'post_id': self.POST.id, })

# Тест для проверки формы создания нового поста (страница /new/)
    def test_post_on_relevant_page(self):
        """Валидная форма создает запись в Post"""

        posts_count = Post.objects.count()
        form_data = {
            'group': self.group.id,
            'text': 'тестовая публикация',
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, HOME_PAGE)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(Post.objects.last().author, self.USER)
        self.assertEqual(Post.objects.last().group.id, self.group.id)
        self.assertEqual(Post.objects.get(text=form_data['text']).text,
                         form_data['text'])

# Тест для проверки меток полей Post
    def test_label(self):
        for title, label in LABELS.items():
            with self.subTest(title=title):
                title_label = self.form.fields[title].label
                self.assertEqual(title_label, label)

    def test_help_text(self):
        for title, label in HELP_TEXTS.items():
            with self.subTest(title=title):
                title_help_text = self.form.fields[title].help_text
                self.assertEqual(title_help_text, label)

    def test_new_and_edit_post_page_shows_correct_context(self):
        """Страница index сформирована правильно через форму"""
        temp_list = [NEW_POST, self.EDIT_PAGE]
        for url in temp_list:
            with self.subTest(url=url):
                response = self.AUTHORIZED_CLIENT.get(url)
                form_fields = {
                    'text': forms.fields.CharField,
                    'group': forms.fields.ChoiceField,
                }
                for value, expected in form_fields.items():
                    with self.subTest(value=value):
                        form_field = response.context['form'].fields[value]
                        self.assertIsInstance(form_field, expected)

    def test_post_edit_by_non_author(self):
        '''При редактировании поста не автором поста
        редактирование не осуществляется'''
        posts_count_before = Post.objects.count()
        new_group = Group.objects.create(title="новая группа",
                                         slug='test_slug2',
                                         description="Тест-описание2")
        form_data = {
            'group': new_group,
            'text': 'тестовая публикация'
        }
        self.AUTHORIZED_CLIENT_2.post(self.EDIT_PAGE,
                                      data=form_data, follow=True)
        self.assertEqual(posts_count_before, Post.objects.count())
        self.assertNotEqual(self.POST.text, form_data['text'])
        self.assertNotEqual(self.POST.group, form_data['group'])
        self.assertNotEqual(self.POST.author, self.username_2)

    def test_post_edit_by_guest(self):
        '''Гость не может редактировать пост'''
        posts_count_before = Post.objects.count()
        new_group = Group.objects.create(title="новая группа",
                                         slug='test_slug2',
                                         description="Тест-описание2")
        form_data = {
            'group': new_group,
            'text': 'тестовая публикация'
        }
        self.GUEST_CLIENT.post(self.EDIT_PAGE,
                               data=form_data, follow=True)
        self.assertEqual(posts_count_before, Post.objects.count())
        self.assertNotEqual(self.POST.text, form_data['text'])
        self.assertNotEqual(self.POST.group, form_data['group'])
