import datetime as dt

from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):

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

    def test_verbose_name(self):
        """verbose_name полей text и group совпадает с ожидаемым"""
        post = PostModelTest.post
        field_verboses = {
            "text": "Текст",
            "group": "Группа", }

        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(post._meta.get_field(value).verbose_name,
                                 expected)

    def test_help_text_name(self):
        """help_text полей text и group совпадает с ожидаемым"""
        post = PostModelTest.post
        field_help_texts = {
            "text": "Придумайте текст для поста",
            "group": "Выберите название группы", }

        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(post._meta.get_field(value).help_text,
                                 expected)

    def test_group_str_method(self):
        """__str__ метод в Group совпадает с ожидаемым"""
        group = PostModelTest.group
        str_text = group.title
        self.assertEqual(group.__str__(), str_text)

    def test_post_str_method(self):
        """__str__ метод в Post сокращает строку text до 15 символов"""
        post = PostModelTest.post
        long_text, short_text = post.text[:16], post.text[:15]
        self.assertTrue(short_text in post.__str__(), "менее 15 символов"
                                                      " или отсутствует")
        self.assertFalse(long_text in post.__str__(), "более 15 символов")
