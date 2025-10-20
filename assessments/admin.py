from django.contrib import admin
from .models import PsychologicalTest, UserResponse

class PsychologicalTestAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at')
    search_fields = ('title',)

class UserResponseAdmin(admin.ModelAdmin):
    list_display = ('user', 'test', 'score', 'created_at')
    list_filter = ('test',)

admin.site.register(PsychologicalTest, PsychologicalTestAdmin)
admin.site.register(UserResponse, UserResponseAdmin)