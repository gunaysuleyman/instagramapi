from django.contrib import admin
from .models import Comment
# Register your models here.

class CommentAdmin(admin.ModelAdmin):
    list_display = ('username', 'text', 'created_at', 'post_link')

admin.site.register(Comment, CommentAdmin)

