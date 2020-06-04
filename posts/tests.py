from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Follow, Group, Post, User

DUMMY_CACHE = {
    'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}
}


class TestProfile(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='sam', email='sam@mail.com', password='12345')
        self.data_registration = {
            'username': 'test_username',
            'password1': '321asdas',
            'password2': '321asdas'
        }

    def test_profile_not_existing_user(self):
        profile_url = reverse('profile',  kwargs={
                              'username': self.data_registration['username']})
        response = self.client.get(profile_url)
        self.assertEqual(response.status_code, 404,
                         msg=('Для несуществующего в базе пользователя '
                              'создается персональная страница(profile)'))

    def test_create_profile_new_registered_user(self):
        profile_url = reverse('profile',  kwargs={
                              'username': self.data_registration['username']})
        response = self.client.get(profile_url)
        self.assertEqual(response.status_code, 404)
        self.client.post(reverse('signup'), self.data_registration,
                         follow=True)
        response = self.client.get(profile_url)
        self.assertEqual(response.status_code, 200,
                         msg=('После регистрации пользователя не создается его'
                              ' персональная страница(profile)'))

    def test_profile_existing_user(self):
        profile_url = reverse(
            'profile', kwargs={'username': self.user.username})
        response = self.client.get(profile_url)
        self.assertEqual(response.status_code, 200,
                         msg=('Не отображается персональная страница '
                              '(profile) существующего в базе пользователя'))


class TestNewPostTempate(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='sam', email='sam@mail.com', password='12345'
        )
        self.post = Post.objects.create(text='текст', author=self.user)
        self.data_page = {'username': self.user.username,
                          'post_id': self.post.id}

    def test_go_page_new_post_unauthorized_user(self):
        new_post_url = reverse('new_post')
        response = self.client.get(new_post_url)
        self.assertRedirects(response,  '/auth/login/?next=/new/',
                             status_code=302, target_status_code=200,
                             msg_prefix=('Неавторизованного пользователя не '
                                         'перенаправляют на страницу входа '
                                         'при переходе на страницу '
                                         'создания новой записи'),
                             fetch_redirect_response=True)

    def test_go_page_edit_post_unauthorized_user(self):
        post_edit_url = reverse('post_edit', kwargs=self.data_page)
        response = self.client.get(post_edit_url)
        self.assertEqual(response.status_code, 302,
                         msg=('Неавторизованный пользователь '
                              'видит форму редактирования чужого поста'))

    def test_go_page_new_post_authorized_user(self):
        self.client.force_login(self.user)
        new_post_url = reverse('new_post')
        response = self.client.get(new_post_url)
        self.assertEqual(response.status_code, 200,
                         msg=('Авторизованный пользователь '
                              'не видит форму создания нового поста'))

    def test_template_new_post_contains(self):
        self.client.force_login(self.user)
        new_post_url = reverse('new_post')
        response = self.client.get(new_post_url)
        self.assertContains(response, 'Новая запись', status_code=200,
                            msg_prefix=('В форму создания поста'
                                        'передается неправильный шаблон'))

    def test_go_page_edit_post_authorized_user(self):
        self.client.force_login(self.user)
        post_edit_url = reverse('post_edit', kwargs=self.data_page)
        response = self.client.get(post_edit_url)
        self.assertEqual(response.status_code, 200,
                         msg=('Авторизованный пользователь '
                              'не видит форму редактирования своего поста'))

    def test_template_edit_post_contains(self):
        self.client.force_login(self.user)
        post_edit_url = reverse('post_edit', kwargs=self.data_page)
        response = self.client.get(post_edit_url)
        self.assertContains(response, 'Редактирование записи', status_code=200,
                            msg_prefix=('В форму редактирования поста'
                                        'передается неправильный шаблон'))


class TestSendFormNewPost(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='sam', email='sam@mail.com', password='12345')
        self.data_post = {'text': 'Привет'}

    def test_create_new_post_unauthorized_user(self):
        new_post_url = reverse('new_post')
        response = self.client.post(new_post_url, self.data_post)
        self.assertRedirects(response,  '/auth/login/?next=/new/',
                             status_code=302, target_status_code=200,
                             msg_prefix=('Неавторизованного пользователя не '
                                         'перенаправляют на страницу входа '
                                         'при попытке заполнить форму '
                                         'публикации новой записи'),
                             fetch_redirect_response=True)
        post = Post.objects.filter(text=self.data_post['text']).exists()
        self.assertFalse(post, msg=('Неавторизованный пользователь'
                                    'смог создать пост'))

    def test__new_post_display_unauthorized_user(self):
        new_post_url = reverse('new_post')
        index_url = reverse('index')
        self.client.post(new_post_url, self.data_post)
        response = self.client.get(index_url)
        self.assertEqual(response.context['paginator'].count, 0,
                         msg=('На главной странице появился пост'
                              'неавторизованного пользователя'))

    def test_create_new_post_authorized_user(self):
        self.client.force_login(self.user)
        new_post_url = reverse('new_post')
        response = self.client.post(new_post_url,  self.data_post)
        self.assertRedirects(response, reverse('index'),
                             status_code=302, target_status_code=200,
                             msg_prefix=('Пользователя не перенаправляют на '
                                         'главную страницу после создания '
                                         ' нового поста'),
                             fetch_redirect_response=True)
        post = Post.objects.filter(text=self.data_post['text']).exists()
        self.assertTrue(post, msg=('Авторизованный пользователь'
                                   'не смог создать пост'))

    def test__new_post_display_authorized_user(self):
        self.client.force_login(self.user)
        new_post_url = reverse('new_post')
        profile_url = reverse(
            'profile', kwargs={'username': self.user.username})
        self.client.post(new_post_url,  self.data_post)
        response = self.client.get(profile_url)
        self.assertEqual(response.context['paginator'].count, 1,
                         msg=('На главной странице не появился пост'
                              'авторизованного пользователя'))


class TestSendFormEditPost(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='sam', email='sam@mail.com', password='12345')
        self.data_post = {'text': 'Привет'}
        self.post = Post.objects.create(text='текст', author=self.user)
        self.data_page = {'username': self.user.username,
                          'post_id': self.post.id}

    @override_settings(CACHES=DUMMY_CACHE)
    def test_edit_post_unauthorized_user(self):
        post_edit_url = reverse('post_edit', kwargs=self.data_page)
        index_url = reverse('index')
        self.client.post(post_edit_url, {'text': 'new'})
        response = self.client.get(index_url)
        self.assertNotContains(response, 'new',  status_code=200,
                               msg_prefix=(
                                   'Неавторизованный пользователь '
                                   'смог изменить пост'))

    def test_contains_edit_post_authorized_user(self):
        self.client.force_login(self.user)
        post_edit_url = reverse('post_edit', kwargs=self.data_page)
        profile_url = reverse(
            'profile', kwargs={'username': self.user.username})
        self.client.post(post_edit_url, {'text': 'new'})
        response = self.client.get(profile_url)
        self.assertEqual(response.context['paginator'].count, 1,
                         msg=('Авторизованный пользователь вместо'
                              'редактирования создал новый пост'))

    def test_edit_post_authorized_user(self):
        self.client.force_login(self.user)
        post_edit_url = reverse('post_edit', kwargs=self.data_page)
        index_url = reverse('index')
        self.client.post(post_edit_url, {'text': 'new'})
        response = self.client.get(index_url)
        self.assertContains(response, text='new', status_code=200,
                            msg_prefix=(
                                'Авторизованный пользователь '
                                'не смог изменить старый пост'))


class TestDisplayNewPostOnPage(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='sam', email='sam@mail.com', password='12345'
        )
        self.client.force_login(self.user)
        self.post = Post.objects.create(text='текст', author=self.user)
        self.data_page = {'username': self.user.username,
                          'post_id': self.post.id}

    def test_dispaly_new_post_index(self):
        index_url = reverse('index')
        response = self.client.get(index_url)
        self.assertContains(response, text=self.post.text, status_code=200,
                            msg_prefix=(
                                'После публикации поста новая запись не '
                                'появляется на главной странице сайта(index)'))

    def test_dispaly_new_post_profile(self):
        profile_url = reverse(
            'profile', kwargs={'username': self.data_page['username']})
        response = self.client.get(profile_url)
        self.assertContains(response, text=self.post.text, status_code=200,
                            msg_prefix=(
                                'После публикации поста новая запись не '
                                'появляется на персональной странице'
                                'пользователя'))

    def test_dispaly_new_post_id(self):
        view_url = reverse('post_view', kwargs=self.data_page)
        response = self.client.get(view_url)
        self.assertContains(response, text=self.post.text, status_code=200,
                            msg_prefix=(
                                'После публикации поста новая запись не '
                                'появляется на отдельной странице поста'))


class TestDisplayEditPostOnPage(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='sam', email='sam@mail.com', password='12345'
        )
        self.post = Post.objects.create(text='текст', author=self.user)
        self.post.text = 'new'
        self.post.save()
        self.client.force_login(self.user)
        self.data_page = {'username': self.user.username,
                          'post_id': self.post.id}

    def test_dispaly_edit_post_index(self):
        index_url = reverse('index')
        response = self.client.get(index_url)
        self.assertContains(response,
                            text='new',
                            status_code=200,
                            msg_prefix=('Cодержимое редактируемого поста не'
                                        'изменилось на главной странице'))

    def test_dispaly_edit_post_profile(self):
        profile_url = reverse(
            'profile', kwargs={'username': self.user.username})
        response = self.client.get(profile_url)
        self.assertContains(response,
                            text='new',
                            status_code=200,
                            msg_prefix=('Cодержимое редактируемого поста не'
                                        'изменилось на странице профиля'))

    def test_dispaly_edit_post_view(self):
        view_url = reverse('post_view', kwargs=self.data_page)
        response = self.client.get(view_url)
        self.assertContains(response,
                            text='new',
                            status_code=200,
                            msg_prefix=('Cодержимое редактируемого поста не'
                                        'изменилось на его отдельной странице'))


class TestPageError(TestCase):
    def setUp(self):
        self.client = Client()

    def test_error_400(self):
        response = self.client.get('/summer/')
        self.assertEqual(response.status_code, 404,
                         msg=('Cервер не возвращает код 404, если'
                              'страница не найдена'))


class TestImage(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='sam', email='sam@mail.com', password='1q2w345'
        )
        self.group = Group.objects.create(title='test', slug='test')
        self.post = Post.objects.create(
            text='текст', author=self.user, group=self.group)
        self.data_page = {'username': self.user.username,
                          'post_id': self.post.id}
        self.client.force_login(self.user)

    def test_page_view_contains_img(self):
        post_edit_url = reverse('post_edit', kwargs=self.data_page)
        view_url = reverse('post_view', kwargs=self.data_page)
        with open('media/posts/test.jpg', 'rb') as img:
            self.client.post(post_edit_url, {'text': 'new', 'image': img})
        tag = 'img'
        response = self.client.get(view_url)
        self.assertContains(response, tag, status_code=200,
                            msg_prefix=('На странице просмотра записи нет'
                                        'тега <<img>>'))

    @override_settings(CACHES=DUMMY_CACHE)
    def test_page_index_contains_img(self):
        post_edit_url = reverse('post_edit', kwargs=self.data_page)
        index_url = reverse('index')
        with open('media/posts/test.jpg', 'rb') as img:
            self.client.post(post_edit_url, {'text': 'new', 'image': img})
        tag = 'img'
        response = self.client.get(index_url)
        self.assertContains(response, tag, status_code=200,
                            msg_prefix=('На главной страницу нет'
                                        'тега <<img>>'))

    def test_page_profile_contains_img(self):
        post_edit_url = reverse('post_edit', kwargs=self.data_page)
        profile_url = reverse(
            'profile', kwargs={'username': self.data_page['username']})
        with open('media/posts/test.jpg', 'rb') as img:
            self.client.post(post_edit_url, {'text': 'new', 'image': img})
        tag = 'img'
        response = self.client.get(profile_url)
        self.assertContains(response, tag, status_code=200,
                            msg_prefix=('На странице профиля нет'
                                        'тега <<img>>'))

    def test_page_group_contains_img(self):
        post_edit_url = reverse('post_edit', kwargs=self.data_page)
        group_url = reverse('group_posts', kwargs={'slug': self.group.slug})
        with open('media/posts/test.jpg', 'rb') as img:
            self.client.post(
                post_edit_url, {'text': 'new',  'group': self.post.id,
                                'image': img})
        tag = 'img'
        response = self.client.get(group_url)
        self.assertContains(response, tag, status_code=200,
                            msg_prefix=('На странице группы нет'
                                        'тега <<img>>'))

    def test_download_not_image(self):
        post_edit_url = reverse('post_edit', kwargs=self.data_page)
        with open('media/posts/оформление.docx', 'rb') as img:
            response = self.client.post(
                post_edit_url, {'text': 'new',
                                'image': img})
        self.assertIn(
            'image', response.context['form'].errors,
            msg='Форма загружает не графический формат')


class TestKacheCache(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='sam', email='sam@mail.com', password='1q2w345'
        )
        self.data_post = {'text': 'Привет'}
        self.client.force_login(self.user)

    def test_index_cashe(self):
        index_url = reverse('index')
        new_post_url = reverse('new_post')
        self.client.post(new_post_url, self.data_post)
        response = self.client.get(index_url)
        self.assertNotContains(
            response, 'Привет', status_code=200,  msg_prefix='Кеширование не работает')


class TestFollow(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_sam = User.objects.create_user(
            username='sam', email='sam@mail.com', password='1q2w345'
        )
        self.user_sara = User.objects.create_user(
            username='sara', email='sara@mail.com', password='3q2w345'
        )
        self.data_page_sara = {'username': self.user_sara.username}
        self.post_sara = Post.objects.create(
            text='текст', author=self.user_sara)
        self.client.force_login(self.user_sam)

    def test_follow_unfollow(self):
        follow_url = reverse(
            'profile_follow',  kwargs=self.data_page_sara)
        self.client.get(follow_url)
        follow = Follow.objects.filter(
            user=self.user_sam,  author=self.user_sara).exists()
        self.assertTrue(follow, msg=('Авторизованный пользователь не может'
                                     'подписываться на других пользователей'))

        unfollow_url = reverse(
            'profile_unfollow',
            kwargs=self.data_page_sara)
        self.client.get(unfollow_url)
        follow = Follow.objects.filter(
            user=self.user_sam,  author=self.user_sara).exists()
        self.assertFalse(follow, msg=('Авторизованный пользователь не может'
                                      'отписаться от пользователя'))

    def test_published_post_from_following_author_on_follow_page(self):
        follow = Follow.objects.create(
            user=self.user_sam,  author=self.user_sara)
        self.assertTrue(follow)
        follow_url = reverse('follow_index')

        response = self.client.get(follow_url)
        self.assertContains(response,
                            text=self.post_sara.text,
                            status_code=200,
                            msg_prefix=('Пост пользователя появился'
                                        'в избранных постах его подписчика'))

    def test_published_post_from_unfollowing_author_on_follow_page(self):
        follow = Follow.objects.filter(
            user=self.user_sam,  author=self.user_sara).exists()
        self.assertFalse(follow)
        follow_url = reverse('follow_index')
        response = self.client.get(follow_url)
        self.assertNotContains(response,
                               text=self.post_sara.text,
                               status_code=200,
                               msg_prefix=('Пост пользователя появился'
                                           'в избранных постах тех, кто на'
                                           'него не подписан'))


class TestComment(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_sam = User.objects.create_user(
            username='sam', email='sam@mail.com', password='1q2w345'
        )
        self.user_sara = User.objects.create_user(
            username='sara', email='sara@mail.com', password='3q2w345'
        )
        self.post_sara = Post.objects.create(
            text='текст', author=self.user_sara)
        self.data_page_sara = {'username': self.user_sara.username,
                               'post_id': self.post_sara.id}

        self.data_comment = {'text': 'Комментарий'}

    def test_comment_authorized_user(self):
        self.client.force_login(self.user_sam)
        post_add_comment = reverse('add_comment', kwargs=self.data_page_sara)
        self.client.post(post_add_comment, self.data_comment)
        post_view_url = reverse(
            'post_view', kwargs=self.data_page_sara)
        response = self.client.get(post_view_url)
        self.assertContains(response,
                            text=self.data_comment['text'],
                            status_code=200,
                            msg_prefix=('Авторизованный пользователь смог'
                                        'оставить комментарий под другим постом'))

    def test_comment_unauthorized_user(self):
        post_add_comment = reverse('add_comment', kwargs=self.data_page_sara)
        self.client.post(post_add_comment, self.data_comment)
        post_view_url = reverse(
            'post_view', kwargs=self.data_page_sara)
        response = self.client.get(post_view_url)
        self.assertNotContains(response,
                               text=self.data_comment['text'],
                               status_code=200,
                               msg_prefix=('Авторизованный пользователь смог'
                                           'оставить комментарий под другим постом'))
