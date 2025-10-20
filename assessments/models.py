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
    
class Assessment(models.Model):
    class Assessment(models.Model):
        response = models.OneToOneField(UserResponse, on_delete=models.CASCADE, related_name='assessment')
        evaluator = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='assessments')
        score = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
        result = models.TextField(blank=True)
        metadata = models.JSONField(null=True, blank=True)
        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now=True)

        def __str__(self):
            return f'Assessment for {self.response.user.username} - {self.response.test.title}'

        class Meta:
            ordering = ['-created_at']
            verbose_name = 'Assessment' 
            verbose_name_plural = 'Assessments'