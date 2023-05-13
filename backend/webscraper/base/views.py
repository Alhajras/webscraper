import logging
import logging.handlers
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
from .models import Crawler, Template, Inspector, Runner, InspectorValue, RunnerStatus
from .pbs.pbs_utils import PBSTestsUtils
from .serializers import (
    CrawlerSerializer,
    UserSerializer,
    TemplateSerializer,
    InspectorSerializer,
    RunnerSerializer,
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
            # TODO: This should return one result only! Use crawler ID, fix it.
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
        all_products = []
        # This is the base URL that the crawler should only crawl from
        base_url = "https://www.flaconi.de"
        # start_url = "https://www.flaconi.de/damen-duftsets/"
        start_url = "https://www.flaconi.de/damen-duftsets/"
        # TODO: Put this in the GUI
        scope_divs = [
            "//*[contains(@class, 'e-tastic__flaconi-product-list')]",
            '//*[@id="app"]/div/main/div/div/div[3]/div',
        ]
        # TODO: Put this in the GUI
        # Urls that may crawler navigate by mistake
        excluded_urls = [
            "https://www.flaconi.de/parfum/",
            "https://www.flaconi.de/damenparfum/",
            "https://www.flaconi.de/damenduefte/",
            "https://www.flaconi.de/damen-duschpflege/",
            "https://www.flaconi.de/damen-parfum-koerperprodukte/",
            "https://www.flaconi.de/damen-deodorant/",
            "https://www.flaconi.de/haarparfum/",
            "https://www.flaconi.de/herrenparfum/",
            "https://www.flaconi.de/unisex-parfum/",
            "https://www.flaconi.de/nischenduefte/",
            "https://www.flaconi.de/haarparfum/",
            "https://www.flaconi.de/herrenparfum/",
            "https://www.flaconi.de/unisex-parfum/",
            "https://www.flaconi.de/nischenduefte/",
        ]
        # Stopping options
        max_pages = crawler.max_pages
        # TODO: Please change this to be read from the request body
        max_visited_links = 5
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
            if len(all_products) >= max_pages:
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
                    title = scoped_element.find_element(
                        By.XPATH, "//*[contains(@class, 'BrandName')]"
                    )
                    all_products.append(title.text)
            except Exception as e:
                print(e)
            for scoped_element in scoped_elements:
                # We add one level
                current_rec_level = link.level + 1
                for href in scoped_element.find_elements(By.CSS_SELECTOR, "a"):
                    # We skip the fragments as they do not add any product, that why we split by #
                    a = href.get_attribute("href").split("#").pop()
                    # Some sites have None values and 'link != a' to avoid looping
                    if a is not None and base_url in a:
                        if a not in excluded_urls:
                            found_link = Link(
                                url=a, visited=False, level=current_rec_level
                            )
                            if (
                                link.url != a
                                and a not in links
                                and len(links) < max_visited_links
                            ):
                                links[a] = found_link
                                q.append(Link(a))
            # TODO: Use `sleep` here
            return find_links()

        runner = Runner.objects.get(id=runner_id)
        runner.status = RunnerStatus.RUNNING
        runner.save()

        q.append(Link(start_url))
        start = time.time()
        find_links()
        inspector = Inspector.objects.all().latest("-id")
        for product in all_products:
            InspectorValue.objects.update_or_create(
                value=product, inspector=inspector, runner=runner
            )
        print(all_products)
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
