from django.db import models
from solo.models import SingletonModel


class RunnerStatus(models.TextChoices):
    NEW = "New"
    RUNNING = "Running"
    COMPLETED = "Completed"
    EXIT = "Exit"
    PAUSED = "Paused"


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


class Crawler(models.Model):
    class Meta:
        ordering = ("created_at",)

    name = models.CharField(max_length=100)
    seed_url = models.TextField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    deleted = models.BooleanField(default=False)
    template = models.OneToOneField(
        Template, on_delete=models.PROTECT, related_name="templates", null=True
    )
    threads = models.PositiveSmallIntegerField(default=2)
    retry = models.PositiveSmallIntegerField(default=2)
    sleep = models.FloatField(default=0.5)
    timeout = models.FloatField(default=10)
    max_pages = models.PositiveIntegerField(default=20)
    max_depth = models.PositiveSmallIntegerField(default=5)
    robot_file_url = models.TextField(default="")
    excluded_urls = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.name


class Runner(models.Model):
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    deleted = models.BooleanField(default=False)
    crawler = models.ForeignKey(Crawler, on_delete=models.PROTECT)
    status = models.CharField(
        max_length=10, choices=RunnerStatus.choices, default=RunnerStatus.NEW
    )

    def __str__(self) -> str:
        return str(self.pk)

    @property
    def collected_documents(self) -> int:
        return InspectorValue.objects.filter(runner=self).count()


class InspectorValue(models.Model):
    class Meta:
        unique_together = ("value", "inspector", "runner")

    value = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    deleted = models.BooleanField(default=False)
    inspector = models.ForeignKey(Inspector, on_delete=models.PROTECT)
    runner = models.ForeignKey(Runner, on_delete=models.PROTECT, default=1)

    def __str__(self) -> str:
        return self.value


class ConfigurationModel(SingletonModel):

    max_num_crawlers = models.PositiveSmallIntegerField(default=2)
    max_num_machines = models.PositiveSmallIntegerField(default=2)
    min_sleep_time = models.FloatField(default=0.25)

    def __str__(self):
        return "Site Configuration"

    class Meta:
        verbose_name = "Site Configuration"
