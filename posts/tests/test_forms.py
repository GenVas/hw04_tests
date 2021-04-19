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
        # первый клиент автор поста
        self.guest_client = Client()
        self.user = User.objects.create_user(username='IvanovI')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.username = self.user.username
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        # второй клиент не автор поста
        self.authorized_client_2 = Client()
        self.user_2 = User.objects.create_user(username='PetrovP')
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.user_2)
        self.username_2 = self.user_2.username

        self.post = Post.objects.create(text=POST_TEST_TEXT,
                                        group=self.group,
                                        author=self.user)
        self.EDIT_PAGE = reverse('post_edit', args=[self.username,
                                                    self.post.id, ])

# Тест для проверки формы создания нового поста (страница /new/)
    def test_post_created_through_valid_form(self):
        """Валидная форма создает запись в Post"""
        form_data = {
            'group': self.group.pk,
            'text': 'тестовая публикация',
        }

        form = PostForm(form_data)
        self.assertTrue(form.is_valid())

        posts_count = Post.objects.count()
        self.authorized_client.post(
            NEW_POST,
            data=form_data,
            follow=True
        )
        post_object = Post.objects.filter(text=form_data['text'],
                                          group=form_data['group'],
                                          author=self.user.id)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(post_object.exists)

    def test_post_not_created_for_invalid_fields(self):
        """Невалидная форма не создает запись в Post"""
        invalid_text = {
            'group': self.group.pk,
            'text': '',
        }
        invalid_group = {
            'group': 'group',
            'text': 'тестовая публикация',
        }
        invalid_data = [invalid_text, invalid_group]
        for invalid in invalid_data:
            form = PostForm(invalid)
            self.assertFalse(form.is_valid())
            posts_count = Post.objects.count()
            self.authorized_client.post(
                reverse('new_post'),
                data=invalid_text,
                follow=True
            )
            try:
                post_object = Post.objects.filter(
                    text=invalid['text'],
                    group=invalid['group'],
                    author=self.user.id
                ).count()
            except ValueError:
                continue
            self.assertEqual(post_object, 0)
            self.assertEqual(Post.objects.count(), posts_count)

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
                response = self.authorized_client.get(url)
                form_fields = {
                    'text': forms.fields.CharField,
                    'group': forms.fields.ChoiceField,
                }
                for value, expected in form_fields.items():
                    with self.subTest(value=value):
                        form_field = response.context['form'].fields[value]
                        self.assertIsInstance(form_field, expected)

    def test_post_edit_by_author(self):
        '''Редактировании поста автором поста
        осуществляется'''
        pk_list_before = Post.objects.filter().values_list('pk', flat=True)
        new_group = Group.objects.create(title="новая группа",
                                         slug='test_slug2',
                                         description="Тест-описание2")
        form_data = {
            'text': 'ну, давай же, редактируйся! Ревьюер требует!',
            'group': new_group.pk,
        }

        self.authorized_client.post(self.EDIT_PAGE,
                                    data=form_data,
                                    follow=False)

        pk_list_after = Post.objects.filter().values_list('pk', flat=True)
        self.assertEqual(set(pk_list_before), set(pk_list_after))
        new_post = Post.objects.get(pk=self.post.id)
        self.assertEqual(new_post.text, form_data['text'])
        self.assertEqual(new_post.group.pk, form_data['group'])
        self.assertEqual(new_post.author.username, self.username)

    def test_post_edit_by_non_author(self):
        '''При редактировании поста не автором поста
        редактирование не осуществляется'''
        pk_list_before = Post.objects.filter().values_list('pk', flat=True)
        new_group = Group.objects.create(title="новая группа",
                                         slug='test_slug2',
                                         description="Тест-описание2")
        form_data = {
            'text': 'это сообщение не должно переписаться в пост',
            'group': new_group.pk,
        }
        self.authorized_client_2.post(self.EDIT_PAGE,
                                      data=form_data,
                                      follow=False)

        pk_list_after = Post.objects.filter().values_list('pk', flat=True)
        self.assertEqual(set(pk_list_before), set(pk_list_after))
        new_post = Post.objects.get(pk=pk_list_after[-0])
        self.assertEqual(new_post.text, self.post.text)
        self.assertEqual(new_post.group.pk, self.post.group.pk)
        self.assertEqual(new_post.author.username, self.username)

    def test_post_edit_by_guest(self):
        '''Гость не может редактировать пост'''
        pk_list_before = Post.objects.filter().values_list('pk', flat=True)
        new_group = Group.objects.create(title="новая группа",
                                         slug='test_slug2',
                                         description="Тест-описание2")
        form_data = {
            'text': 'это сообщение не должно переписаться в пост',
            'group': new_group.pk,
        }
        self.guest_client.post(self.EDIT_PAGE,
                               data=form_data,
                               follow=False)

        pk_list_after = Post.objects.filter().values_list('pk', flat=True)
        self.assertEqual(set(pk_list_before), set(pk_list_after))
        new_post = Post.objects.get(pk=pk_list_after[-0])
        self.assertEqual(new_post.text, self.post.text)
        self.assertEqual(new_post.group.pk, self.post.group.pk)
        self.assertEqual(new_post.author.username, self.username)
