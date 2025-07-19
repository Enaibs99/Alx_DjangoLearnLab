
# relationship_app/query_samples.py

from relationship_app.models import Author, Book, Library, Librarian

# 1. Query all books by a specific author
def books_by_author(author_name):
    try:
        author = Author.objects.get(name=author_name)
        books = Book.objects.filter(author=author)
        return books
    except Author.DoesNotExist:
        return []

# 2. List all books in a library
def books_in_library(library_name):
    try:
        library = Library.objects.get(name=library_name)
        return library.books.all()
    except Library.DoesNotExist:
        return []

# 3. Retrieve the librarian for a library
def librarian_for_library(library_name):
    try:
        library = Library.objects.get(name=library_name)
        return Librarian.objects.get(library=library)
    except (Library.DoesNotExist, Librarian.DoesNotExist):
        return None


# SAMPLE USAGE — only for testing in Django shell
if __name__ == "__main__":
    print("Books by 'Chinua Achebe':")
    for book in books_by_author("Chinua Achebe"):
        print("-", book.title)

    print("\nBooks in 'Main Campus Library':")
    for book in books_in_library("Main Campus Library"):
        print("-", book.title)

    print("\nLibrarian of 'Main Campus Library':")
    librarian = librarian_for_library("Main Campus Library")
    print(librarian.name if librarian else "No librarian found.")
