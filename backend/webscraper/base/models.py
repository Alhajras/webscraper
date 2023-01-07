from django.db import models


class SpiderStatus(models.TextChoices):
    NEW = "new"
    RUNNING = "running"
    COMPLETED = "completed"
    EXIT = "exit"


class Template(models.Model):
    class Meta:
        ordering = ("created_at",)

    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name


class Inspector(models.Model):
    class Meta:
        ordering = ("created_at",)

    name = models.CharField(max_length=100)
    selector = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted = models.BooleanField(default=False)
    template = models.ForeignKey(Template, on_delete=models.PROTECT)

    def __str__(self) -> str:
        return self.name


class Spider(models.Model):
    class Meta:
        ordering = ("created_at",)

    name = models.CharField(max_length=100)
    url = models.TextField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    deleted = models.BooleanField(default=False)
    template = models.OneToOneField(
        Template, on_delete=models.PROTECT, related_name="templates", null=True
    )
    status = models.CharField(
        max_length=10, choices=SpiderStatus.choices, default=SpiderStatus.NEW
    )

    def __str__(self) -> str:
        return self.name
