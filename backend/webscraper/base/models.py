from django.db import models


class RunnerStatus(models.TextChoices):
    NEW = "new"
    RUNNING = "running"
    COMPLETED = "completed"
    EXIT = "exit"
    PAUSED = "paused"


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

    def __str__(self) -> str:
        return self.name


class Runner(models.Model):
    class Meta:
        ordering = ("created_at",)

    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    deleted = models.BooleanField(default=False)
    spider = models.ForeignKey(Spider, on_delete=models.PROTECT)
    status = models.CharField(
        max_length=10, choices=RunnerStatus.choices, default=RunnerStatus.NEW
    )

    def __str__(self) -> str:
        return str(self.pk)
