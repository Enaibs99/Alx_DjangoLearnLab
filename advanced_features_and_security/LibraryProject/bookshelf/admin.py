from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Book
from .models import BookAdmin 
from django.utils.translation import gettext_lazy

# Register your models here.
from .models import Book

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publication_year')  # Show these fields in admin list
    search_fields = ('title', 'author')                     # Enable search by title and author
    list_filter = ('publication_year',)                     # Add a filter sidebar for publication 
    
    class CustomUserAdmin(UserAdmin):
        model = CustomUser
        list_display = ['Username', 'email', 'date_of_birth', 'is_staff']
        fieldsets = UserAdmin.fieldsets + (
            (gettext_lazy('Additional info'), {'fields': ('date_of_birth', 'profile_photo')}),
        
        )
        add_fieldsets = UserAdmin.add_fieldsets + (
           (gettext_lazy('Additional Info'), {'fields': ('date_of_birth', 'profile_photo')}),
        )

    admin.site.register(Book, BookAdmin)
    admin.site.register(CustomUser, CustomUserAdmin)