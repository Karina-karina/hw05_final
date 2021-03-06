from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True, db_index=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='author_posts')
    group = models.ForeignKey(Group, on_delete=models.SET_NULL,
                              blank=True, null=True,
                              related_name='group_posts')
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text


class Comment(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comment')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comment')
    text = models.TextField()
    created = models.DateTimeField('date published', auto_now_add=True)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follower')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following')

    def __str__(self):
        return f'follower - {self.user} following - {self.author}'


class Like(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='post_like')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user_like')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='author_like')

    def __str__(self):
        return f'user_like - {self.user} author_like - {self.author} post_like - {self.post}'
