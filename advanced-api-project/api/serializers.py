from rest_framework import serializers
from .models import Author, Book
import datetime

class BookSerializer(serializers.ModelSerializer):
    """
    Serializer for the Book model.
    - Serializes all fields of the Book model.
    - Includes a custom validator to ensure publication_year is not in the future.
    """
     
    class Meta:
        model = Book
        fields = '__all__'  # includes: title, publication_year, author

    def validate_publication_year(self, value):
        """
        Custom validator for publication_year.
        Ensures the year is not greater than the current year.
        """

        current_year = datetime.datetime.now().year
        if value > current_year:
            raise serializers.ValidationError("Publication year cannot be in the future.")
        return value
class AuthorSerializer(serializers.ModelSerializer):
    books = BookSerializer(many=True, read_only=True)
    """
    Serializer for the Author model.
    - Serializes 'id', 'name', and a nested list of books using BookSerializer.
    - The nested 'books' field uses the related_name from the Book model.
    - read_only=True: Books are displayed but not created through this serializer.
    """

    class Meta:
        model = Author
        fields = ['id', 'name', 'books']