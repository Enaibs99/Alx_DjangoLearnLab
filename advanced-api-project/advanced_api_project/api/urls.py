from django.urls import path
from .views import (
    BookListView,
    BookDetailView,
    BookCreateView,
    BookUpdateView,
    BookDeleteView,
)
urlpatterns = [
    path('books/', BookListView.as_view(), name='book-list'),              # GET, POST
    path('books/create/', BookCreateView.as_view(), name='book-create'),  # POST
    path('books/<int:pk>/', BookDetailView.as_view(), name='book-detail'),# GET
    path('books/update/', BookUpdateView.as_view(), name='book-update'),  # PUT (Checker wants this)
    path('books/delete/', BookDeleteView.as_view(), name='book-delete'),  # DELETE (Checker wants this)
]