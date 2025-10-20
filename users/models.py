from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class CustomUser(AbstractUser):
    # Дополнительные поля для профиля пользователя
    date_of_birth = models.DateField(null=True, blank=True)
    bio = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.username

class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    preferences = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.user.username}'s Profile"
    
class User(models.Model):
    """
    Простой модель-представление пользователя для CRUD в этом API.
    (Если у вас уже есть отдельная пользователи/app с кастомным AUTH_USER_MODEL,
    используйте её вместо этой модели.)
    """
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    profile = models.JSONField(default=dict, blank=True)  # психологический профиль и т.п.
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.email