from time import sleep
from typing import Callable, Union, Any

from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from selenium.common import TimeoutException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlparse

from .filters import InspectorFilter
from .models import Crawler, Template, Inspector, Runner
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
    queryset = Runner.objects.filter(deleted=False)
    serializer_class = RunnerSerializer
    filter_backends = [DjangoFilterBackend]

    @action(detail=False, url_path="start", methods=["post"])
    def start(self, request: Request) -> Response:
        links: dict[str, Link] = {}
        q = []
        all_products = []
        # This is the base URL that the crawler should only crawl from
        base_url = "https://www.flaconi.de"
        # start_url = "https://www.flaconi.de/damen-duftsets/"
        start_url = "https://www.flaconi.de/damen-duftsets/"
        scope_divs = ["//*[contains(@class, 'e-tastic__flaconi-product-list')]", '//*[@id="app"]/div/main/div/div/div[3]/div']

        # Urls that may crawler navigate by mistake
        excluded_urls = [""]
        # Stopping options
        max_pages = 200
        max_visited_links = 24
        visited_list_counter = 0
        max_rec_level = 1
        base_urlparse = urlparse(base_url)

        # Define Browser Options
        chrome_options = Options()
        user_agent = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2'
        chrome_options.add_argument(f'user-agent={user_agent}')
        chrome_options.add_argument("--window-size=2560,1440")
        chrome_options.add_argument("--headless")  # Hides the browser window
        # Reference the local Chromedriver instance
        chrome_path = r"/usr/local/bin/chromedriver"
        driver = webdriver.Chrome(
            executable_path=chrome_path, options=chrome_options
        )

        def find_links(link: Link, cookies_button: str = ''):
            # We stop recursion when we reach tha mx level of digging into pages
            if link.level > max_rec_level:
                pass
            # Run the Webdriver, save page an quit browser
            driver.get(link.url)
            # wait_until(
            #     driver,
            #     expected_conditions.presence_of_element_located(
            #         (By.CSS_SELECTOR, cookies_button)
            #     ),
            #     "Cookies button was never found.",
            # )
            # driver.find_element(By.CSS_SELECTOR, cookies_button).click()
            # This should be configured
            driver.refresh()
            scoped_elements = []
            try:
                # This is to click on the cookies button
                # wait_until(
                #     driver,
                #     expected_conditions.presence_of_element_located(
                #         (By.CSS_SELECTOR, ".product-detail-info__header-name")
                #     ),
                #     "Cookies button was never found.",
                #     timeout=3,
                # )
                # import pdb
                # pdb.set_trace()
                for scope_div in scope_divs:
                    try:
                        scoped_elements.append(driver.find_element(By.XPATH, scope_div))
                    except Exception as e:
                        pass
                for scoped_element in scoped_elements:
                    title = scoped_element.find_element(By.XPATH, "//*[contains(@class, 'BrandName')]")
                    all_products.append(title.text)
            except Exception as e:
                print(e)

            for scoped_element in scoped_elements:
                # We add one level
                current_rec_level = link.level + 1
                for href in scoped_element.find_elements(By.CSS_SELECTOR, "a"):
                    # We skip the fragments as they do not add any product, that why we split by #
                    a = href.get_attribute("href").split('#').pop()
                    # Some sites have None values and 'link != a' to avoid looping
                    if a is not None and base_url in a:
                        found_link = Link(url=a, visited=False, level=current_rec_level)
                        if link.url != a and a not in links:
                            links[a] = found_link
                            q.append(a)
            return

        def wait_until(
            driver,
            condition: Callable[[WebDriver], bool],
            failure_msg: Union[str, Callable[[], str]],
            timeout: int = 10,
            *,
            ignored_exceptions: Any | None = None,
        ) -> None:
            """
            Do nothing until some condition is met
            :param condition: See :ref:`expected conditions <selenium:waits>`
            :param failure_msg: The test failure message to use if the condition is never met
               (or a callable that generates one)
            :param timeout: How long to wait before giving up, in seconds
            :param ignored_exceptions: Allows to ignore certain exceptions while polling.
            :return:
            """
            wait = WebDriverWait(driver, timeout, ignored_exceptions=ignored_exceptions)
            try:
                wait.until(condition)
            except TimeoutException:
                print("This page does not contain the selector given.")

        q.append(start_url)
        while len(q) != 0 and len(all_products) < max_pages and visited_list_counter < max_visited_links:
            try:
                url = q.pop(0)
                visited_list_counter += 1
                find_links(Link(url))
                print(url)
                print(all_products)

            except Exception as e:
                print(f"I am done {q}")

        print(all_products)
        driver.quit()
        return Response(status=200)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
