from django.db import models
from django.utils import timezone


class User(models.Model):
    """
    Простая модель пользователя для CRUD в API.
    Не используется для аутентификации (только как сущность в базе).
    """
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    profile = models.JSONField(default=dict, blank=True)  # психологический профиль и т.п.
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    """
    Дополнительный профиль пользователя (например, предпочтения или демографические данные).
    """
    GENDER_CHOICES = [
        ("M", "Male"),
        ("F", "Female"),
        ("O", "Other"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile_details")
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    preferences = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.user.email}'s Profile"
