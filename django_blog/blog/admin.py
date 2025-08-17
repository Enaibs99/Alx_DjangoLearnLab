from django.contrib import admin
from .models import Post
from .models import Comment
from .models import Tag

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'published_date')
    list_filter = ('status', 'published_date', 'author')
    search_fields = ('title', 'content')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("post", "author", "created_at")
    search_fields = ("content", "author_username", "post_title" )
    list_filter = ("created_at", "author")


admin.site.register(Tag)
