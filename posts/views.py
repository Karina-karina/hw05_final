from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def index(request):
    post_list = Post.objects.order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html',
                  {'page': page,
                   'paginator': paginator}, content_type='text/html',
                  status=200)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.group_posts.order_by('-pub_date')[:12]
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html',
                  {'page': page,
                   'group': group,
                   'paginator': paginator}, content_type='text/html',
                  status=200)


@login_required
def new_post(request):
    form = PostForm()
    if request.method == 'POST':
        form = PostForm(request.POST or None,
                        files=request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
        return render(request, 'new_post.html', {'form': form}, content_type='text/html',
                      status=200)
    return render(request, 'new_post.html', {'form': form}, content_type='text/html',
                  status=200)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts_author = author.author_posts.order_by('-pub_date')
    paginator = Paginator(posts_author, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'profile.html',
                  {'page': page,
                   'author': author,
                   'paginator': paginator}, content_type='text/html',
                  status=200)


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(author.author_posts, id=post_id)
    form = CommentForm()
    comments = post.comment.order_by('-created')
    return render(request, 'post.html',
                  {'post': post,
                   'author': author,
                   'form': form,
                   'items': comments}, content_type='text/html',
                  status=200)


def post_edit(request, username, post_id):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        return redirect('post_view', username, post_id)

    post = get_object_or_404(author.author_posts, id=post_id)
    form = PostForm(instance=post)

    if request.method == 'POST':
        form = PostForm(request.POST or None,
                        files=request.FILES or None, instance=post)
        if form.is_valid():
            form.save()
            return redirect('post_view', username, post_id)
        return render(request, 'new_post.html', {'form': form},
                      )
    return render(request, 'new_post.html',
                  {'form': form,
                   'post': post,
                   'author': author},)


def page_not_found(request, exception):
    return render(request, 'misc/404.html',
                  {'path': request.path}, status=404)


def server_error(request):
    return render(request, 'misc/500.html', status=500)


@login_required
def add_comment(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(author.author_posts, id=post_id)
    form = CommentForm()
    if request.method == 'POST':
        form = CommentForm(request.POST or None)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
    return redirect('post_view', username, post_id)


@login_required
def follow_index(request):
    follow = Follow.objects.filter(user=request.user).all()
    authors = (f.author for f in follow)
    post_list = Post.objects.filter(
        author__in=authors).order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request,  'follow.html',
                  {'page': page,
                   'paginator': paginator}, content_type='text/html',
                  status=200)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(user=request.user,  author=author).exists()
    if follow:
        return redirect('profile', username=username)
    else:
        if request.user != author:
            Follow.objects.create(user=request.user,  author=author)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(user=request.user,  author=author).exists()
    if follow:
        Follow.objects.filter(user=request.user,  author=author).delete()
    return redirect('profile', username=username)
