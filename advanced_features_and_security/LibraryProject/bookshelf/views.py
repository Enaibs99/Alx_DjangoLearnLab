from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from relationship_app.models import Book
from django.http import HttpResponseBadRequest
from .forms import ExampleForm
# Create your views here.

def book_list(request):
    books = Book.objects.all()
    return render(request, 'bookshelf/book_list.html', {'books': books})
@login_required
@permission_required('relationship_app.can_add_book', raise_exception=True)
def add_book(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('author')
        if title and author:
            Book.objects.create(title=title, author=author)
            return redirect('book_list')
        return render(request, 'bookshelf/add_book.html')
    @login_required
    @permission_required('relationship_app.can_delete_book', raise_exception=True)
    def delete_book(request, pk):
         book = get_object_or_404(Book, pk=pk)
         if request.method == 'POST':
             book.delete()
             return redirect('book_list')
         return render(request, 'bookshelf/delete_book.html', {'book': book})
    def search_books(request):
        query = request.GET.get('q', '')
        if not query.isalnum():  # Input validation
            return HttpResponseBadRequest("Invalid input")
        results = Book.objects.filter(title__icontains=query)  # ORM: SQL-safe
        return render(request, 'bookshelf/book_list.html', {'books': results})