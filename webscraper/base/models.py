from django.db import models

# Create your models here.
class Spider(models.Model):
    class Meta:
        ordering = ("created_at",)

    name = models.CharField(max_length=100)
    url = models.TextField(blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField()
