from django.urls import path

from . import views


urlpatterns = [
    path('', views.home, name='home'),

    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    path('post/create/', views.create_post, name='create_post'),
    path('post/<int:post_id>/like/', views.like_post, name='like_post'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),

    path(
        'profile/<str:username>/',
        views.profile,
        name='profile'
    ),

    path(
        'profile/<str:username>/follow/',
        views.follow_user,
        name='follow_user'
    ),
    path(
        'post/<int:post_id>/delete/',
        views.delete_post,
        name='delete_post'
    ),
    path(
        'profile/photo/update/',
        views.update_profile_photo,
        name='update_profile_photo'
    ),
]