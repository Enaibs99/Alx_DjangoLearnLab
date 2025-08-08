from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from .models import Book, Author  # Adjust import if needed
from django.urls import reverse
from rest_framework.authtoken.models import Token

class BookAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.login(username="testuser", password="testpass")
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        