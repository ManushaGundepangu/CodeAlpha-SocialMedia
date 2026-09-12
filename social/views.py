from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from .models import Comment, Follow, Like, Post, Profile


def home(request):
    posts = Post.objects.select_related('user').prefetch_related(
        'comments__user',
        'likes'
    ).annotate(
        like_count=Count('likes', distinct=True),
        comment_count=Count('comments', distinct=True)
    )

    users = User.objects.all().order_by('username')

    liked_post_ids = set()

    if request.user.is_authenticated:
        liked_post_ids = set(
            Like.objects.filter(
                user=request.user,
                post__in=posts
            ).values_list('post_id', flat=True)
        )

    return render(
        request,
        'social/home.html',
        {
            'posts': posts,
            'users': users,
            'liked_post_ids': liked_post_ids,
        }
    )

def register(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if not username or not password:
            messages.error(request, 'Username and password are required.')
        elif password != confirm_password:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            Profile.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('home')

    return render(request, 'social/register.html')


def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('home')

        messages.error(request, 'Invalid username or password.')

    return render(request, 'social/login.html')


@login_required
def user_logout(request):
    logout(request)
    return redirect('login')


@login_required
def create_post(request):
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        image = request.FILES.get('image')

        if content or image:
            Post.objects.create(
                user=request.user,
                content=content,
                image=image
            )
            messages.success(request, 'Post published successfully!')
        else:
            messages.error(request, 'Please write something or select an image.')

    return redirect('home')


@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # Check whether the current user already liked this post
    already_liked = Like.objects.filter(
        user=request.user,
        post=post
    ).exists()

    if already_liked:
        messages.info(request, "You already liked this post ❤️")
    else:
        Like.objects.create(
            user=request.user,
            post=post
        )
        messages.success(request, "Post liked ❤️")

    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()

        if content:
            Comment.objects.create(
                post=post,
                user=request.user,
                content=content
            )

    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def profile(request, username):
    profile_user = get_object_or_404(User, username=username)

    posts = Post.objects.filter(
        user=profile_user
    ).select_related('user').annotate(
        like_count=Count('likes', distinct=True),
        comment_count=Count('comments', distinct=True)
    )

    followers_count = Follow.objects.filter(
        following=profile_user
    ).count()

    following_count = Follow.objects.filter(
        follower=profile_user
    ).count()

    is_following = Follow.objects.filter(
        follower=request.user,
        following=profile_user
    ).exists()

    return render(
        request,
        'social/profile.html',
        {
            'profile_user': profile_user,
            'posts': posts,
            'followers_count': followers_count,
            'following_count': following_count,
            'is_following': is_following,
        }
    )


@login_required
def follow_user(request, username):
    target_user = get_object_or_404(User, username=username)

    if target_user != request.user:
        follow, created = Follow.objects.get_or_create(
            follower=request.user,
            following=target_user
        )

        if not created:
            follow.delete()

    return redirect('profile', username=username)

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.user != request.user:
        messages.error(request, "You can only delete your own posts.")
        return redirect('home')

    post.delete()
    messages.success(request, "Post deleted successfully.")

    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def update_profile_photo(request):
    profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    if request.method == 'POST':
        image = request.FILES.get('profile_image')

        if image:
            profile.profile_image = image
            profile.save()
            messages.success(
                request,
                'Profile photo updated successfully!'
            )
        else:
            messages.error(
                request,
                'Please select an image.'
            )

    return redirect('profile', username=request.user.username)