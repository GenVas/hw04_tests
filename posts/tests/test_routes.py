from django.test import TestCase
from django.urls import reverse

from posts.models import Group, Post, User

HOME_PAGE, NEW_POST = reverse('index'), reverse('new_post')


class RoutesTest(TestCase):

    def setUp(self):

        user = User.objects.create_user(username='test_user')
        group = Group.objects.create(title='группа',
                                     description='описание',
                                     slug='group')
        post = Post.objects.create(text='тестовая публикация',
                                   group=group,
                                   author=user)
        self.GROUP_POSTS = reverse('group_posts', kwargs={'slug': group.slug})
        self.PROFILE = reverse('profile', kwargs={'username': user.username})
        self.VIEW_POST = reverse('post', kwargs={'username':
                                                 post.author.username,
                                                 'post_id': post.id})
        self.POST_EDIT = reverse('post_edit', kwargs={'username':
                                                      post.author.username,
                                                      'post_id': post.id})

    def test_routes(self):
        test_urls = {HOME_PAGE: '/',
                     NEW_POST: '/new/',
                     self.GROUP_POSTS: '/group/group/',
                     self.PROFILE: '/test_user/',
                     self.VIEW_POST: '/test_user/1/',
                     self.POST_EDIT: '/test_user/1/edit/', }
        for page, url in test_urls.items():
            self.assertEqual(page, url)
