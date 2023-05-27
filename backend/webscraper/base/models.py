from django.db import models
from django.db.models import Count
from solo.models import SingletonModel


class RunnerStatus(models.TextChoices):
    NEW = "New"
    RUNNING = "Running"
    COMPLETED = "Completed"
    EXIT = "Exit"
    PAUSED = "Paused"

class IndexerStatus(models.TextChoices):
    NEW = "New"
    RUNNING = "Running"
    COMPLETED = "Completed"
    EXIT = "Exit"

class InspectorAttributes(models.TextChoices):
    HREF = "href"
    NAME = "name"
    SRC = "src"
    TITLE = "title"
    VALUE = "value"


class Template(models.Model):
    class Meta:
        ordering = ("created_at",)

    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    data = models.JSONField()


class Indexer(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    deleted = models.BooleanField(default=False)
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True),
    status = models.CharField(
        max_length=10, choices=IndexerStatus.choices, default=IndexerStatus.NEW
    )

    def __str__(self) -> str:
        return self.name

    @property
    def inspectors_to_be_indexed(self):
        return Inspector.objects.filter(indexer=self).values_list('id', flat=True)


class Inspector(models.Model):
    class Meta:
        ordering = ("created_at",)

    name = models.CharField(max_length=100)
    selector = models.TextField()
    attribute = models.CharField(max_length=25, choices=InspectorAttributes.choices, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted = models.BooleanField(default=False)
    template = models.ForeignKey(Template, on_delete=models.PROTECT)
    indexer = models.ForeignKey(Indexer, on_delete=models.PROTECT, null=True)

    def __str__(self) -> str:
        return self.name


class Crawler(models.Model):
    class Meta:
        ordering = ("created_at",)

    name = models.CharField(max_length=100)
    seed_url = models.TextField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
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
    robot_file_url = models.TextField(default="", blank=True)
    excluded_urls = models.TextField(blank=True)
    scope_divs = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.name


class Runner(models.Model):
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    deleted = models.BooleanField(default=False)
    crawler = models.ForeignKey(Crawler, on_delete=models.PROTECT)
    name = models.CharField(max_length=50, default='New runner')
    status = models.CharField(
        max_length=10, choices=RunnerStatus.choices, default=RunnerStatus.NEW
    )

    def __str__(self) -> str:
        return str(self.pk)

    @property
    def collected_documents(self) -> int:
        return InspectorValue.objects.filter(runner=self).values('url').annotate(dcount=Count('url')).count()

    @property
    def current_crawled_url(self) -> int:
        return InspectorValue.objects.filter(runner=self).values('url').last()


class InspectorValue(models.Model):
    class Meta:
        # TODO: This makes it slower I have to check this by using URLS.
        unique_together = ("inspector", "runner", "url")

    value = models.TextField(blank=True)
    url = models.URLField(default='')
    attribute = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted = models.BooleanField(default=False)
    inspector = models.ForeignKey(Inspector, on_delete=models.PROTECT)
    runner = models.ForeignKey(Runner, on_delete=models.PROTECT, default=1)

    def __str__(self) -> str:
        return f"Runner: {self.runner}, Inspector: ({self.inspector.name}),  value: {self.value}, attribute: {self.attribute}"


class ConfigurationModel(SingletonModel):

    max_num_crawlers = models.PositiveSmallIntegerField(default=2)
    max_num_machines = models.PositiveSmallIntegerField(default=2)
    min_sleep_time = models.FloatField(default=0.25)

    def __str__(self):
        return "Site Configuration"

    class Meta:
        verbose_name = "Site Configuration"
