from bookshelf.models import Book book = Book.objects.create(title="1984", author="George Orwell", publication_year=1949) print(book)

Output: 1984 by George Orwellretrieved = Book.objects.get(id=book.id)
print(retrieved.title, retrieved.author, retrieved.publication_year)

Output: 1984 George Orwell 1949
retrieved.title = "Nineteen Eighty-Four" retrieved.save() print(retrieved.title)

Output: Nineteen Eighty-Four
retrieved.delete() print(Book.objects.all())

Output: <QuerySet []>