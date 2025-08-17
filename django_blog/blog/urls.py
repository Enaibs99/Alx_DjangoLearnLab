from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import (
    PostListView,
    PostDetailView,
    PostCreateView,
    PostUpdateView,
    PostDeleteView,

)

urlpatterns = [

    # Registration
    path ('',views.home, name='home'),
    path ('register/', views.register, name='register'),
    path ('profile/', views.profile, name='profile'),

    # Login & Logout (with Django's built-in auth views)
    path('login/', auth_views.LoginView.as_view(template_name='blog/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='blog/logout.html'), name='logout'),

    path ('post/', PostListView.as_view(), name= 'post_list'),

    path('post/<int:pk>/', PostDetailView.as_view(), name="post-detail"),
    path('post/new/', PostCreateView.as_view(), name="post-create"),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name="post-update"),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name="post-delete"),

    path('post/<int:pk>/comments/new/', views.add_comment, name='comment-create'),
    path('comment/<int:pk>/update/', views.edit_comment, name='edit-comment'),
    path('comment/<int:pk>/delete/', views.delete_comment, name='delete-comment'),

    path('tags/<str:tag_name>/', views.posts_by_tag, name='posts-by-tag'),
    path('search/',views.search_posts, name='search-posts'),
    path('tags/<slug:tag_slug>/', views.PostByTagListView.as_view(), name='posts_by_tag'),
    
]