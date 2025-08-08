from django.db import models

# Create your models here.
class Author(models.Model):
    name = models.CharField(max_length=100)
    # This model represents an author in the system.
    # It contains only a 'name' field for simplicity.
    def __str__(self):
        return self.name
    
    class Book(models.Model):
    # This model represents a book.
    # Each book is associated with one author (ForeignKey).
        title = models.CharField(max_length=200)
        publication_year = models.IntegerField()
        author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    # ForeignKey creates a one-to-many relationship:
    # One author -> Many books.
    # related_name='books' lets us access all books of an author via author.books.all()

        def __str__(self):
             return f"{self.title} ({self.publication_year})"
    