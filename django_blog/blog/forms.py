from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Post
from .models import Comment
from taggit.forms import TagWidget

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Required. Enter a valid email address.")

    class Meta:
        model= User
        fields = ("username", "email", "password1", "password2")

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model= User
        fields = ['first_name', 'last_name', 'email']

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'tags']
        widgets = {
            'tags': TagWidget(),
        }

class CommentForm(forms.ModelForm):
    content = forms.CharField(
        label="Your Comment",
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Write your comment here..."}),
        min_length=2
    )
    class Meta:
         model = Comment
         fields = ['content'] 

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if len(content.strip()) < 2:
             raise forms.ValidationError("Comment is too short!")
        return content



    