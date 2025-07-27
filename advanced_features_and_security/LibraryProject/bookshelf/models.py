from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import BaseUserManager, AbstractUser
from django.contrib.auth.models import CustomUserManager 

# Create your models here.
class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    publication_year = models.IntegerField()

    def __str__(self):
        return f"{self.title} by {self.author}"
    
    class Meta:
        permission = [
            ('can_view', 'can view books'),
            ('can_create', 'can create books'),
            ('can_edit', 'can edit books'),
            ('can_delete','can delete books'),
        ]
    class CustomUserManager(BaseUserManager):
       def create_user(self, username, email, password=None, **extra_fields):
          if not email:
            raise ValueError("Users must have an email address")
          email = self.normalize_email(email)
          user = self.model(username=username, email=email, **extra_fields)
          user.set_password(password)
          user.save(using=self._db)
          return user
       
       def create_superuser(self, username, email, password=None, **extra_fields):
            extra_fields.setdefault('is_staff', True)
            extra_fields.setdefault('is_superuser', True)

            if not extra_fields.get('is_staff'):
              raise ValueError("Superuser must have is is_staff=True.")
            if not extra_fields.get("is_superuser"):
              raise ValueError("Superuser must have is_superuser=True.")

            return self.create_user(username, email, password, **extra_fields)
       
    class CustomUser(AbstractUser):
       email = models.EmailField(unique=True)
       date_of_birth = models.DateField(null=True, blank=True)
       profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
       is_staff = models.BooleanField(default=False)
       is_active = models.BooleanField(default=True)

       objects = CustomUserManager()

    def __str__(self):
        return self.username