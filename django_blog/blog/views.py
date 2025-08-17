from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .forms import UserUpdateForm
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import Post, Comment
from .forms import CommentForm
from .forms import PostForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, get_object_or_404, redirect
from taggit.models import Tag
from .models import Post
from django.urls import reverse_lazy
from django.db.models import Q

def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("profile") 
    else:
        form = CustomUserCreationForm()
    return render(request, "blog/register.html", {"form": form})

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated!")
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'blog/profile.html', {'form': form})
class CustomLoginView(LoginView):
    template_name = "blog/login.html"

class CustomLogoutView(LogoutView):
    template_name = "blog/logout.html"

def home(request):
    return render(request, 'blog/home.html')
def posts(request):
    return render(request, 'blog/posts.html')

class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts' 
    ordering = ['-date_posted']    

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Post.objects.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(tags__name__icontains=query)
            ).distinct()
        return Post.objects.all()
    

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context['comments'] = post.comments.all()
        context['form'] = CommentForm()
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = self.object
            comment.author = request.user
            comment.save()
            messages.success(request, "Your comment has been added!")
            return redirect('post-detail', pk=self.object.pk)
        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)
    

class PostCreateView(CreateView):
        model = Post
        fields = ["title", "content", "status"]
        template_name = 'blog/post_form.html'

        def form_valid(self, form):
            form.instance.author = self.request.user
            return super().form_valid(form)
        
class PostUpdateView(UpdateView):
        model = Post
        fields = ["title", "content", 'status']
        template_name = 'blog/post_form.html'

        def form_valid(self, form):
            form.instance.author = self.request.user
            return super().form_valid(form)
        
        def test_func(self):
            post = self.get_object()
            return self.request.user == post.author
        

class PostDeleteView(DeleteView):
        model = Post
        template_name = 'blog/post_confirm_delete.html'
        success_url = reverse_lazy('posts')

        def test_func(self):
            post = self.get_object()
            return self.request.user == post.author
    
        def blog_list(request):
         posts = Post.objects.all()
         print(posts)

@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.save()
                messages.success(request, "Your comment has been added!")
                return redirect('post-detail', pk=post.pk)
            else:
             form = CommentForm()
            return render(request, 'blog/add_comment.html', {'form': form, 'post': post})
    
@login_required
def edit_comment(request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        if comment.author != request.user:
            messages.error(request, "You do not have permission to edit this comment.")
            return redirect('post-detail', pk=comment.post.pk)
        
        if request.method == 'POST':
            form = CommentForm(request.POST, instance=comment)
            if form.is_valid():
                form.save()
                messages.success(request, "Comment updated successfully!")
                return redirect('post-detail', pk=comment.post.pk)
        else:
             form = CommentForm(instance=comment)
        return render(request, 'blog/edit_comment.html', {'form': form, 'comment': comment})
    
@login_required
def delete_comment(request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        if comment.author != request.user:
            messages.error(request, "You do not have permission to delete this comment.")
            return redirect('post-detail', pk=comment.post.pk)
        
        if request.method == 'POST':
            post_pk = comment.post.pk
            comment.delete()
            messages.success(request, "Comment deleted successfully!")
            return redirect('post-detail', pk=post_pk)
        
        return render(request, 'blog/delete_comment.html', {'comment': comment})
    
class CommentCreateView(LoginRequiredMixin, CreateView):
         model = Comment
         fields = ['content']
         template_name = 'blog/comment_form.html'

         def form_valid(self, form):
             form.instance.author = self.request.user
             form.instance.post_id = self.kwargs['pk']
             return super().form_valid(form)
    
class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
        model = Comment
        fields = ['content']
        template_name = 'blog/comment_form.html'

        def test_func(self):
            comment = self.get_object()
            return self.request.user == comment.author
        
class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
        model = Comment
        template_name = 'blog/comment_confirm_delete.html'

        def get_success_url(self):
            return reverse_lazy('post-detail', kwargs={'pk': self.object.post.pk})
        
        def test_func(self):
            comment = self.get_object()
            return self.request.user == comment.author
        
        def search_posts(request):
             query = request.GET.get('q')
             results = Post.objects.all()
             if query:
                 results = results.filter(
                     Q(title__icontains=query) |
                     Q(content__icontains=query) |
                     Q(tags__name__icontains=query)
                  ).distinct()
             return render(request, 'blog/search_results.html', {'results': results})
        
        def posts_by_tag(request, tag_name):
            tag =  get_object_or_404(Tag, name=tag_name)
            posts = Post.objects.filter( "blog/posts_by_tag.html", {"tag": tag, "posts": posts})
            return render(request, 'blog/post_list.html', {'posts': posts, 'tag': tag_name})
        
        def search_posts(request):
            query = request.GET.get('q', '').strip()
            posts = Post.objects.filter(status='published')
            if query:
                posts = posts.filter(
                     Q(title__icontains=query) |
                     Q(content__icontains=query) |
                     Q(tags__name__icontains=query)
                ).distinct().order_by('-published_date')
                return render(request, 'blog/search_results.html', {'posts': posts, 'query': query})

             








    



