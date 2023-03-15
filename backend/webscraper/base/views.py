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
from .models import Spider, Template, Inspector, Runner
from .serializers import (
    SpiderSerializer,
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


class SpiderViewSet(EverythingButDestroyViewSet):
    queryset = Spider.objects.filter(deleted=False)
    serializer_class = SpiderSerializer


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
    def __init__(self, url: urlparse, visited: bool = False):
        self.url = url
        self.visited = visited


class RunnerViewSet(EverythingButDestroyViewSet):
    queryset = Runner.objects.filter(deleted=False)
    serializer_class = RunnerSerializer
    filter_backends = [DjangoFilterBackend]

    @action(detail=False, url_path="start", methods=["post"])
    def start(self, request: Request) -> Response:
        links: dict[str, Link] = {}
        q = []
        all_products = []
        base_url = "https://www.zara.com/de/en/"
        start_url = "https://www.zara.com/de/en/waxed-effect-parka-p02969309.html?v1=178821511&v2=2105310"
        base_urlparse = urlparse(base_url)

        def find_links(link: Link, cookies_button: str):
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
            # Run the Webdriver, save page an quit browser
            driver.get(link.url)
            wait_until(
                driver,
                expected_conditions.presence_of_element_located(
                    (By.CSS_SELECTOR, cookies_button)
                ),
                "Cookies button was never found.",
            )
            driver.find_element(By.CSS_SELECTOR, cookies_button).click()
            # This should be configured
            driver.refresh()
            try:
                wait_until(
                    driver,
                    expected_conditions.presence_of_element_located(
                        (By.CSS_SELECTOR, ".product-detail-info__header-name")
                    ),
                    "Cookies button was never found.",
                    timeout=3,
                )
                title = driver.find_element(
                    By.CSS_SELECTOR, ".product-detail-info__header-name"
                )
                all_products.append(title.text)
            except Exception as e:
                print(e)

            for href in driver.find_elements(By.CSS_SELECTOR, "a"):
                # We skip the fragments as they do not add any product, that why we split by #
                a = href.get_attribute("href").split('#').pop()git
                # Some sites have None values and 'link != a' to avoid looping
                if a is not None and base_url in a:
                    found_link = Link(url=a, visited=False)
                    if link.url != a and a not in links:
                        links[a] = found_link
                        q.append(a)
            driver.quit()
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

        while len(q) != 0:
            try:
                url = q.pop(0)
                find_links(Link(url), cookies_button="#onetrust-accept-btn-handler")
                print(url)
                print(all_products)

            except Exception as e:
                print(f"I am done {q}")

        print(all_products)

        return Response(status=200)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
