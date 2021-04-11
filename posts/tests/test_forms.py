import datetime as dt

from django.test import Client, TestCase
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from posts.forms import PostForm
from posts.models import Group, Post, User


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(title="Тест-название",
                                         slug='test_slug',
                                         description="Тест-описание")
        cls.form = PostForm()

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='IvanovI')

        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        slug = self.group.slug
        self.url_names = {
            'index.html': reverse('index'),
            'group.html': reverse('group_posts', kwargs={'slug': slug}),
            'new.html': reverse('new_post')}

        self.labels = {
            'group': _('Вы можете выбрать группу'),
            'text': _('Напишите сообщение')
        }
        self.help_texts = {
            'group': 'Поле не является обязательным',
            'text': _('Придумайте текст для поста. '
                      'Поле обязательно для заполнения'),
        }
# Тест для проверки формы создания нового поста (страница /new/)

    def test_post_on_relevant_page(self):
        """Валидная форма создает запись в Post"""

        posts_count = Post.objects.count()
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
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), posts_count + 1)

# Тест для проверки меток полей Post
    def test_label(self):
        for title, label in self.labels.items():
            with self.subTest(title=title):
                title_label = self.form.fields[title].label
                self.assertEqual(title_label, label)

    def test_help_text(self):
        for title, label in self.help_texts.items():
            with self.subTest(title=title):
                title_help_text = self.form.fields[title].help_text
                self.assertEqual(title_help_text, label)
