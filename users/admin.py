from django.contrib import admin
from .models import UserProfile,CustomUser


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_of_birth', 'gender')
    search_fields = ('user__username', 'gender')


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'first_name', 'last_name', 'created_at')
    search_fields = ('email', 'first_name', 'last_name')



admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(CustomUser, UserAdmin)
