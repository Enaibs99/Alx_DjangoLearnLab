from django.urls import path, include
from .views import RegisterView, LoginView, UserProfileView
from django.contrib import admin
from . import views
from .views import FollowUserView, UnfollowUserView


urlpatterns = [
     path('register/', views.RegisterView.as_view(), name='register'),
     path('login/', LoginView.as_view(), name='login'),
     path('profile/', UserProfileView.as_view(), name='profile'),
     path("follow/<int:user_id>/", FollowUserView.as_view(), name="follow-user"),
     path("unfollow/<int:user_id>/", UnfollowUserView.as_view(), name="unfollow-user"),
] 