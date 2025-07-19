from django.shortcuts import render
from .models import Book

def list_books(request):
    books = Book.objects.all()  # <-- REQUIRED
    return render(request, "relationship_app/list_books.html", {"books": books})  

from django.views.generic.detail import DetailView
from .models import Library

class LibraryDetailView(DetailView):
    model = Library
    template_name = "relationship_app/library_detail.html"  # <== this exact string is required
    context_object_name = "library"

# Create your views here.
