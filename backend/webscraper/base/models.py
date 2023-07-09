from django.db import models
from django.db.models import Count
from polymorphic.models import PolymorphicModel
from solo.models import SingletonModel
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class RunnerStatus(models.TextChoices):
    NEW = "New"
    RUNNING = "Running"
    COMPLETED = "Completed"
    EXIT = "Exit"
    PAUSED = "Paused"


class IndexerStatus(models.TextChoices):
    NEW = "New"
    DICTIONARY = "Dictionary"
    INDEXING = "Indexing"
    COMPLETED = "Completed"
    EXIT = "Exit"


class InspectorAttributes(models.TextChoices):
    HREF = "href"
    NAME = "name"
    SRC = "src"
    TITLE = "title"
    VALUE = "value"


class InspectorTypes(models.TextChoices):
    IMAGE = "image"
    TEXT = "text"
    LINK = "link"


class ActionTypes(models.TextChoices):
    CLICK = "click"
    WAIT = "wait"
    SCROLL = "scroll"


class CrawlingAlgorithms(models.TextChoices):
    """
    This is used to declare the supported parsing algorithms
    """

    BFS_TOP_DOWN = "BFS_TOP_DOWN"
    BFS_BOTTOM_UP = "BFS_BOTTOM_UP"


class ActionChainEvent(models.TextChoices):
    BEFORE = "before"
    AFTER = "after"


class ScrollDirection(models.TextChoices):
    UP = "up"
    DOWN = "down"


class Template(models.Model):
    class Meta:
        ordering = ("created_at",)

    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name


class Indexer(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    b_parameter = models.FloatField(default=0.75)
    k_parameter = models.FloatField(default=1.75)
    q_gram_use_synonym = models.BooleanField(default=True)
    q_gram_q = models.SmallIntegerField(default=3)
    dictionary = models.CharField(default="wikidata-entities.tsv", max_length=200)
    skip_words = models.TextField(blank=True)
    small_words_threshold = models.PositiveSmallIntegerField(default=0)
    completed_at = models.DateTimeField(blank=True, null=True)
    deleted = models.BooleanField(default=False)
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=10, choices=IndexerStatus.choices, default=IndexerStatus.NEW
    )

    def __str__(self) -> str:
        return self.name

    @property
    def inspectors_to_be_indexed(self):
        return Inspector.objects.filter(indexer=self).values_list("id", flat=True)


class Inspector(models.Model):
    class Meta:
        ordering = ("created_at",)

    name = models.CharField(max_length=100)
    selector = models.TextField()
    attribute = models.CharField(
        max_length=25, choices=InspectorAttributes.choices, blank=True, default=""
    )
    type = models.CharField(
        max_length=10,
        choices=InspectorTypes.choices,
        blank=True,
        default=InspectorTypes.TEXT,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    deleted = models.BooleanField(default=False)
    template = models.ForeignKey(Template, on_delete=models.PROTECT)
    indexer = models.ForeignKey(Indexer, on_delete=models.PROTECT, null=True)

    def __str__(self) -> str:
        return self.name

    @property
    def template_name(self):
        return self.template.name


class ActionChain(models.Model):
    name = models.CharField(max_length=100, default="default-actions")
    disabled = models.BooleanField(default=True)
    template = models.ForeignKey(Template, on_delete=models.PROTECT)
    event = models.CharField(
        max_length=10, choices=ActionChainEvent.choices, default=ActionChainEvent.BEFORE
    )

    def __str__(self) -> str:
        return self.name


class Action(PolymorphicModel):
    name = models.CharField(max_length=50)
    type = models.CharField(
        max_length=10, choices=ActionTypes.choices, default=ActionTypes.CLICK
    )
    action_chain = models.ForeignKey(ActionChain, on_delete=models.PROTECT)
    order = models.PositiveIntegerField(default=1)
    deleted = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name


class ScrollAction(Action):
    times = models.PositiveIntegerField(default=1)
    direction = models.CharField(
        max_length=10, choices=ScrollDirection.choices, default=ScrollDirection.DOWN
    )


class ClickAction(Action):
    selector = models.TextField()


class WaitAction(Action):
    time = models.FloatField(default=1)


class Document(models.Model):
    """
    Document represent the saved results of template,
    for example one movie, onr product or one-page result count as one document.
    """

    template = models.ForeignKey(Template, on_delete=models.PROTECT, null=True)


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
    max_collected_docs = models.PositiveIntegerField(default=20)
    max_pages = models.PositiveIntegerField(default=20)
    show_browser = models.BooleanField(default=False)
    max_depth = models.PositiveSmallIntegerField(default=5)
    robot_file_url = models.TextField(default="", blank=True)
    allow_multi_elements = models.BooleanField(default=False)
    excluded_urls = models.TextField(blank=True)
    scope_divs = models.TextField(blank=True)
    parsing_algorithm = models.CharField(
        max_length=20,
        choices=CrawlingAlgorithms.choices,
        default=CrawlingAlgorithms.BFS_BOTTOM_UP,
    )

    def __str__(self) -> str:
        return self.name


class Runner(models.Model):
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    deleted = models.BooleanField(default=False)
    crawler = models.ForeignKey(Crawler, on_delete=models.PROTECT)
    name = models.CharField(max_length=50, default="New runner")
    status = models.CharField(
        max_length=10, choices=RunnerStatus.choices, default=RunnerStatus.NEW
    )
    machine = models.CharField(max_length=225, default="localhost")

    def __str__(self) -> str:
        return str(self.pk)

    @property
    def collected_documents(self) -> int:
        return (
            InspectorValue.objects.filter(deleted=False, runner=self)
            .values("document__id")
            .annotate(dcount=Count("id"))
            .count()
        )

    @property
    def current_crawled_url(self) -> int:
        return InspectorValue.objects.filter(runner=self).values("url").last()


class LinkFragment(models.Model):
    fragment = models.CharField(max_length=100)
    parent = models.ForeignKey('self', on_delete=models.PROTECT, null=True)
    runner = models.ForeignKey(Runner, on_delete=models.PROTECT)

    @property
    def full_url(self):
        full_url = self.fragment
        parent = self.parent
        while parent is not None:
            full_url = f"{parent.fragment}/{full_url}"
            parent = parent.parent
        return full_url


class InspectorValue(models.Model):
    value = models.TextField(blank=True)
    url = models.URLField(default="")
    link_fragment = models.ForeignKey(LinkFragment, on_delete=models.PROTECT)
    attribute = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    deleted = models.BooleanField(default=False)
    inspector = models.ForeignKey(Inspector, on_delete=models.PROTECT)
    runner = models.ForeignKey(Runner, on_delete=models.PROTECT, default=1)
    document = models.ForeignKey(Document, on_delete=models.PROTECT, default=1)

    def __str__(self) -> str:
        return (
            f"Runner: {self.runner},"
            f" Inspector: ({self.inspector.name}),  value: {self.value}, attribute: {self.attribute}"
        )

    @property
    def type(self):
        return self.inspector.type

    @property
    def table_header(self):
        return self.inspector.name


class ConfigurationModel(SingletonModel):
    max_num_crawlers = models.PositiveSmallIntegerField(default=2)
    max_num_machines = models.PositiveSmallIntegerField(default=2)
    min_sleep_time = models.FloatField(default=0.25)

    def __str__(self):
        return "Site Configuration"

    class Meta:
        verbose_name = "Site Configuration"
