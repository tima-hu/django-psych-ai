from django.contrib import admin
from .models import UserProfile

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_of_birth', 'gender')
    search_fields = ('user__username', 'gender')

admin.site.register(UserProfile, UserProfileAdmin)