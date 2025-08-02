from .models import Book
from rest_framework import serializers
from django.db import models

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['title', 'author']