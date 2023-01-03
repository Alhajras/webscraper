from django.db import models


class SpiderStatus(models.TextChoices):
    NEW = "new"
    RUNNING = "running"
    COMPLETED = "completed"
    EXIT = "exit"


# Create your models here.
class Spider(models.Model):
    class Meta:
        ordering = ("created_at",)

    name = models.CharField(max_length=100)
    url = models.TextField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True)
    deleted = models.BooleanField(default=False)
    status = models.CharField(
        max_length=10, choices=SpiderStatus.choices, default=SpiderStatus.NEW
    )

    def __str__(self) -> str:
        return self.name
