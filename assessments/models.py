from django.db import models
from django.contrib.auth.models import User

class PsychologicalTest(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class UserResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(PsychologicalTest, on_delete=models.CASCADE)
    answers = models.JSONField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Response by {self.user.username} for {self.test.title}'