from django.db import models

class Comment(models.Model):
    username = models.CharField(max_length=100)
    full_name = models.CharField(max_length=100, default='')
    text = models.TextField()
    created_at = models.DateTimeField()
    post_link = models.URLField()

def __str__(self):
    return self.username
