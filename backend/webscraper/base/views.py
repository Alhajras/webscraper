import logging
import logging.handlers

from django.core.serializers import serialize
from django.utils import timezone
import time

from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlparse

from .filters import InspectorFilter
from .indexing.inverted_index import InvertedIndex
from .models import Crawler, Template, Inspector, Runner, InspectorValue, RunnerStatus, Indexer, IndexerStatus
from .pbs.pbs_utils import PBSTestsUtils
from .serializers import (
    CrawlerSerializer,
    UserSerializer,
    TemplateSerializer,
    InspectorSerializer,
    RunnerSerializer, IndexerSerializer, InspectorValueSerializer,
)


class EverythingButDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    pass


class CrawlerViewSet(EverythingButDestroyViewSet):
    queryset = Crawler.objects.filter(deleted=False)
    serializer_class = CrawlerSerializer


class TemplateViewSet(EverythingButDestroyViewSet):
    queryset = Template.objects.filter(deleted=False)
    serializer_class = TemplateSerializer


class IndexerViewSet(EverythingButDestroyViewSet):
    queryset = Indexer.objects.filter(deleted=False).order_by("-id")
    serializer_class = IndexerSerializer

    def create(self, request: Request, *args, **kwargs) -> Response:
        """
        Create an index but without running it.
        """
        indexer = super().create(request, *args, **kwargs)
        inspectors_ids = [selector['id'] for selector in request.data['selected_inspectors']]
        Inspector.objects.filter(id__in=inspectors_ids).update(indexer=indexer.data['id'])
        return indexer

    @action(detail=False, url_path="start", methods=["post"])
    def start(self, request: Request) -> Response:
        indexer_id = request.data['id']
        Indexer.objects.filter(id=indexer_id).update(status=IndexerStatus.RUNNING)
        inverted_index = InvertedIndex()
        inverted_index.create_index(indexer_id)
        runner_serializer = RunnerSerializer(data=request.data)
        indexer = Indexer.objects.get(id=indexer_id)
        indexer.status = IndexerStatus.COMPLETED
        indexer.completed_at = timezone.now()
        indexer.save()
        return Response(status=200)

    @action(detail=True, url_path="search", methods=["POST"])
    def search(self, request: Request, pk: int) -> Response:
        query = request.data['q'].lower().strip()
        inverted_index = InvertedIndex()
        result = inverted_index.process_query(query.split(" "), pk)
        results = InspectorValue.objects.filter(id__in=result).values_list('url', flat=True)
        products = []
        for p in results:
            products.append(InspectorValue.objects.filter(url=p).values('value', 'url', 'inspector', 'attribute'))
        return Response(data=products)


class InspectorViewSet(EverythingButDestroyViewSet):
    queryset = Inspector.objects.filter(deleted=False)
    serializer_class = InspectorSerializer
    filterset_class = InspectorFilter
    filter_backends = [DjangoFilterBackend]
    filterset_fields = "template"


class Link:
    def __init__(self, url: urlparse, visited=False, level=0):
        self.url = url
        self.visited = visited
        self.level = level


class RunnerViewSet(EverythingButDestroyViewSet):
    queryset = Runner.objects.filter(deleted=False).order_by("-id")
    serializer_class = RunnerSerializer
    filter_backends = [DjangoFilterBackend]

    @action(detail=False, url_path="submit", methods=["post"])
    def submit(self, request: Request) -> Response:
        runner_serializer = RunnerSerializer(data=request.data)
        # TODO: If data are invalid we should throw an error here
        if not runner_serializer.is_valid():
            pass
        # IP address are taken from the docker/.env file
        pbs_head_node = "173.16.38.8"
        pbs_sim_node = "173.16.38.9"
        pbs = PBSTestsUtils(pbs_head_node=pbs_head_node, pbs_sim_node=pbs_sim_node)
        pbs.set_up_pbs()
        runner_serializer = RunnerSerializer(data=request.data)
        if runner_serializer.is_valid():
            runner_serializer.save()

        # TODO: If data are invalid we should throw an error here
        if not runner_serializer.is_valid():
            pass

        pbs.run_job(runner_serializer.data)

        return Response(status=200)

    @action(detail=True, url_path="stop", methods=["post"])
    def stop(self, request: Request, pk: int) -> Response:
        runner = Runner.objects.get(pk=pk)
        runner.status = str(RunnerStatus.EXIT)
        runner.save()
        return Response(status=200)

    @action(detail=False, url_path="start", methods=["post"])
    def start(self, request: Request) -> Response:
        runner_id = request.data['id']
        runner_serializer = RunnerSerializer(data=request.data)
        # TODO: If data are invalid we should throw an error here
        if not runner_serializer.is_valid():
            pass
        print(runner_serializer.data)
        crawler = Crawler.objects.get(pk=runner_serializer.data["crawler"])

        def create_logger() -> logging:
            """
            Creates a logger for the runner to log the history  of the crawler runner.
            :return:
            """
            runner = Runner.objects.get(id=runner_id)
            filename = f"{runner.id}.runner.log"
            logger = logging.getLogger()
            logger.setLevel(logging.INFO)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )

            handler = logging.handlers.RotatingFileHandler(
                filename, mode="w", backupCount=5
            )
            handler.setLevel(logging.INFO)
            handler.setFormatter(formatter)
            logger.addHandler(handler)

            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            ch.setFormatter(formatter)
            logger.addHandler(ch)
            return logger

        logger = create_logger()
        links: dict[str, Link] = {}
        q = []
        # This is the base URL that the crawler should only crawl from
        base_url = "https://www.flaconi.de"
        # start_url = "https://www.flaconi.de/damen-duftsets/"
        start_url = crawler.seed_url
        # scope_divs = [
        #     "//*[contains(@class, 'e-tastic__flaconi-product-list')]",
        #     '//*[@id="app"]/div/main/div/div/div[3]/div',
        # ]
        # TODO: Use a better splitter
        # Urls that may crawler navigate by mistake
        excluded_urls = crawler.excluded_urls.split("\";\"")
        scope_divs = crawler.scope_divs.split("\";\"")
        # Stopping options
        max_pages = crawler.max_pages
        # TODO: Please change this to be read from the request body
        max_visited_links = crawler.max_pages
        max_rec_level = crawler.max_depth
        base_urlparse = urlparse(base_url)
        # Define Browser Options
        chrome_options = Options()
        user_agent = (
            "Mozilla/5.0 (Windows NT 6.1)"
            " AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2"
        )
        chrome_options.add_argument(f"user-agent={user_agent}")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--window-size=2560,1440")
        chrome_options.add_argument("--headless")  # Hides the browser window
        # Reference the local Chromedriver instance
        chrome_path = r"/usr/bin/chromedriver"
        driver = webdriver.Chrome(executable_path=chrome_path, options=chrome_options)

        def find_links():
            # TODO: This should return one result only! Use crawler ID, fix it.
            runner = Runner.objects.get(id=runner_id)

            if runner.status == str(RunnerStatus.EXIT):
                return
            if len(q) == 0:
                return
            link: Link = q.pop()
            if runner.collected_documents >= max_pages:
                return
            print(link.url)
            logger.info(link.url)
            # We stop recursion when we reach tha mx level of digging into pages
            if link.level > max_rec_level:
                return
            # Run the Webdriver, save page an quit browser
            # TODO: I should use `retry` here
            driver.get(link.url)
            # This should be configured
            scoped_elements = []
            try:
                for scope_div in scope_divs:
                    try:
                        scoped_elements.append(driver.find_element(By.XPATH, scope_div))
                    except Exception:
                        pass
                for scoped_element in scoped_elements:
                    # We start looking up for the elements we would like to collect inside the page/document
                    inspectors_list = Inspector.objects.filter(template=crawler.template)
                    for inspector in inspectors_list:
                        inspector_element = scoped_element.find_element(
                            By.XPATH, inspector.selector
                        )
                        InspectorValue.objects.update_or_create(
                            url=link.url,
                            attribute=inspector_element.get_attribute(inspector.attribute),
                            value=inspector_element.text, inspector=inspector, runner=runner
                        )
            except Exception as e:
                print(e)
            for scoped_element in scoped_elements:
                # We add one level
                current_rec_level = link.level + 1
                for a in scoped_element.find_elements(By.CSS_SELECTOR, "a"):
                    # We skip the fragments as they do not add any product, that why we split by #
                    if a.get_attribute("href") is None:
                        continue
                    href = a.get_attribute("href").split("#").pop()
                    print(href)
                    # Some sites have None values and 'link != a' to avoid looping
                    if href is not None and base_url in href:
                        if href not in excluded_urls:
                            found_link = Link(
                                url=href, visited=False, level=current_rec_level
                            )
                            if (
                                link.url != href
                                and href not in links
                                and len(links) < max_visited_links
                            ):
                                links[href] = found_link
                                q.append(Link(href))
            # TODO: Use `sleep` here
            return

        runner = Runner.objects.get(id=runner_id)
        runner.status = RunnerStatus.RUNNING
        runner.created_at = timezone.now()
        runner.save()

        q.append(Link(start_url))
        start = time.time()
        while len(q) != 0:
            find_links()
        print(runner.collected_documents)
        end = time.time()
        print(end - start)
        driver.quit()
        runner.status = RunnerStatus.COMPLETED
        runner.completed_at = timezone.now()
        runner.save()
        logger.info(f"Runner #{runner.id} is completed...")
        logger.info(f"Runner #{runner.id} is completed. Time consumed {end - start}")
        return Response(status=200)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
