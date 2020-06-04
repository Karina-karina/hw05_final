from django.forms import ModelForm

from .models import Comment, Post


class PostForm(ModelForm):

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Ваш пост',
            'group': 'Группа',
            'image': 'Изображение'
        }
        help_texts = {
            'text': 'Чем бы вы хотели поделиться?',
            'group': 'Нажмите, чтобы выбрать группу',
            'image': 'Загрузите изображение',
        }


class CommentForm(ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
        help_texts = {
            'text': 'Введите ваш комментарий',
        }
