import logging
import logging.handlers
import random
import re
import threading
from concurrent.futures import ThreadPoolExecutor, Future, wait

from django.utils import timezone
import time

from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from selenium.webdriver.common.by import By
from .dataclasses import *
from .filters import InspectorFilter
from .indexing.inverted_index import InvertedIndex
from .models import (
    Crawler,
    Template,
    Inspector,
    Runner,
    InspectorValue,
    RunnerStatus,
    Indexer,
    IndexerStatus,
    Action,
)
from .pbs.pbs_utils import PBSTestsUtils
from .serializers import (
    CrawlerSerializer,
    UserSerializer,
    TemplateSerializer,
    InspectorSerializer,
    RunnerSerializer,
    IndexerSerializer,
    ActionPolymorphicSerializer,
)
from .utils import (extract_disallow_lines_from_url, find_the_links_current_level, add_link_to_level,
                    split_work_between_threads, create_chrome_driver, all_threads_completed)


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
        inspectors_ids = [
            selector["id"] for selector in request.data["selected_inspectors"]
        ]
        Inspector.objects.filter(id__in=inspectors_ids).update(
            indexer=indexer.data["id"]
        )
        return indexer

    @action(detail=False, url_path="available-indexers", methods=["GET"])
    def available_indexers(self, request: Request) -> Response:
        inverted_index = InvertedIndex()
        serialized_indexers = [
            IndexerSerializer(indexer).data
            for indexer in inverted_index.cached_indexers_keys()
        ]
        return Response(status=200, data=serialized_indexers)

    @action(detail=False, url_path="start", methods=["post"])
    def start(self, request: Request) -> Response:
        indexer_id = request.data["id"]
        Indexer.objects.filter(id=indexer_id).update(status=IndexerStatus.RUNNING)
        inverted_index = InvertedIndex()
        inverted_index.create_index(indexer_id)
        indexer = Indexer.objects.get(id=indexer_id)
        indexer.status = IndexerStatus.COMPLETED
        indexer.completed_at = timezone.now()
        indexer.save()
        return Response(status=200)

    @action(detail=True, url_path="search", methods=["POST"])
    def search(self, request: Request, pk: int) -> Response:
        query = request.data["q"].lower().strip()
        inverted_index = InvertedIndex()
        result = inverted_index.process_query(query.split(" "), pk)
        results = InspectorValue.objects.filter(id__in=result).values_list(
            "url", flat=True
        )
        products = []
        for p in results:
            products.append(
                InspectorValue.objects.filter(url=p).values(
                    "value", "url", "inspector", "attribute"
                )
            )
        return Response(data=products)


class InspectorViewSet(EverythingButDestroyViewSet):
    queryset = Inspector.objects.filter(deleted=False)
    serializer_class = InspectorSerializer
    filterset_class = InspectorFilter
    filter_backends = [DjangoFilterBackend]
    filterset_fields = "template"


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
        runner_id = request.data["id"]
        runner_serializer = RunnerSerializer(data=request.data)
        # TODO: If data are invalid we should throw an error here
        if not runner_serializer.is_valid():
            pass

        crawler = Crawler.objects.get(pk=runner_serializer.data["crawler"])

        # def execute_all_before_actions() -> None:
        #     template = crawler.template
        #     actions_chain = ActionChain.objects.get(template=template)
        #     all_actions = Action.objects.filter(action_chain=actions_chain).filter(deleted=False).order_by("order")
        #     for action_to_be_excuted in all_actions:
        #         if isinstance(action_to_be_excuted, ClickAction):
        #             driver.find_element(
        #                 By.XPATH, action_to_be_excuted.selector
        #             ).click()
        #         elif isinstance(action_to_be_excuted, WaitAction):
        #             time.sleep(action_to_be_excuted.time)
        #         elif isinstance(action_to_be_excuted, ScrollAction):
        #             for _ in range(action_to_be_excuted.times):
        #                 body = driver.find_element(By.CSS_SELECTOR, "body")
        #                 body.send_keys(Keys.END)
        #                 # We give time for the loading before scrolling again
        #                 time.sleep(1000)

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

        # This dictionary contain all the queues shared between threads
        shared_threads_pool: dict[int, CrawlerThread] = {}
        start = time.time()
        # Define Browser Options
        threads_metrics = {}

        # TODO: Use a better splitter
        # Urls that may crawler navigate by mistake
        excluded_urls = crawler.excluded_urls.split('";"')
        robot_disallow_links = [
            re.escape(bad_link)
            for bad_link in extract_disallow_lines_from_url(crawler.robot_file_url)
        ]
        # Make a regex that matches if any of our regexes match.
        disallow_link_patterns = ""
        if len(robot_disallow_links) != 0:
            disallow_link_patterns = "(" + ")|(".join(robot_disallow_links) + ")"

        scope_divs = crawler.scope_divs.split('";"')
        # Stopping options
        max_collected_docs = crawler.max_collected_docs
        max_visited_links = crawler.max_pages
        max_rec_level = crawler.max_depth

        def crawl_seed(seed: str):
            thread_id = threading.get_native_id()
            # print(f"Thread: {thread_id} started! Seed: {seed}")
            driver = create_chrome_driver()

            # This will hold all the queues for all the links different levels
            links_queues: dict[int, list] = {}
            crawler_thread = CrawlerThread(thread_id=thread_id, running=True, queues=links_queues)

            if thread_id not in shared_threads_pool:
                shared_threads_pool[thread_id] = crawler_thread

            # This is the base URL that the crawler should only crawl from
            base_url = urlparse(seed).hostname
            # start_url = "https://www.flaconi.de/damen-duftsets/"
            start_url = seed
            current_active_queue = []

            def find_links() -> None:
                shared_threads_pool[thread_id].running = True
                runner = Runner.objects.get(id=runner_id)

                if runner.status == str(RunnerStatus.EXIT):
                    return

                if len(current_active_queue) == 0:
                    return

                # TODO: This should be configurable
                link: Link = current_active_queue.pop()
                if runner.collected_documents >= max_collected_docs:
                    return
                logger.info(f"Thread: {thread_id} - {link.url} out of {len(current_active_queue)}")
                # We stop recursion when we reach tha mx level of digging into pages
                if link.level > max_rec_level:
                    return
                # Run the Webdriver, save page an quit browser
                # TODO: I should use `retry` here
                # print(f"Thread: {thread_id} is loading page {link.url}")
                if links[link.url].visited:
                    return
                driver.get(link.url)
                links[link.url].visited = True
                # time.sleep(random.random())
                # We execute all the before actions before we start crawling
                # execute_all_before_actions()
                # This should be configured
                scoped_elements = []
                try:
                    for scope_div in scope_divs:
                        try:
                            # print(f"Thread: {thread_id} is looking for scope elements.")
                            scoped_elements.append(driver.find_element(By.XPATH, scope_div))
                        except Exception as e:
                            print(f"Thread id: {crawler_thread.thread_id} had an error, scope not found.")
                            pass

                    # We add one layer of depth
                    current_rec_level = link.level + 1
                    for scoped_element in scoped_elements:
                        # We add one level
                        all_links_in_the_page = scoped_element.find_elements(By.CSS_SELECTOR, "a")
                        for a in all_links_in_the_page:
                            if a.get_attribute("href") is None:
                                continue
                            # We skip the fragments as they do not add any product, that why we split by #
                            href = a.get_attribute("href").split("#").pop()
                            # Respect the Robots.txt file protocol
                            if disallow_link_patterns != "" and re.match(
                                    disallow_link_patterns, href
                            ):
                                continue
                            # Skip unwanted links
                            if href in excluded_urls:
                                continue
                            # Links from outside the main host are skipped
                            if base_url != urlparse(href).hostname:
                                continue
                            if (
                                    link.url != href
                                    and href not in links
                                    and len(links) < max_visited_links
                            ):
                                found_link = Link(url=href, visited=False, level=current_rec_level)
                                links[href] = found_link
                                add_link_to_level(links_queues, found_link)
                    for scoped_element in scoped_elements:
                        # We start looking up for the elements we would like to collect inside the page/document
                        inspectors_list = Inspector.objects.filter(
                            template=crawler.template
                        )
                        documents_dict = {}
                        for inspector in inspectors_list:
                            inspector_elements = scoped_element.find_elements(
                                By.XPATH, inspector.selector
                            )

                            if len(inspector_elements) == 0:
                                return
                            documents_dict[inspector] = []
                            # TODO: this should be configurable
                            allow_multi_elements = False
                            if not allow_multi_elements:
                                inspector_elements = [inspector_elements[0]]
                            for inspector_element in inspector_elements:
                                attribute = ''
                                if inspector.attribute != '':
                                    attribute = inspector_element.get_attribute(
                                        inspector.attribute
                                    )
                                if thread_id not in threads_metrics:
                                    threads_metrics[thread_id] = 1
                                else:
                                    threads_metrics[thread_id] = threads_metrics[thread_id] + 1
                                threads_metrics[thread_id] += 1
                                documents_dict[inspector].append(InspectorValue(url=link.url,
                                                                                attribute=attribute,
                                                                                value=inspector_element.text,
                                                                                inspector=inspector,
                                                                                runner=runner,))

                        lengths = [len(doc) for doc in documents_dict.values()]
                        if not all(list_size == lengths[0] for list_size in lengths):
                            logger.info(f"Thread: {thread_id} - The URL: {link.url} has different inspectors lists.")
                            return

                        # We start saving documents
                        for inspector in documents_dict.values():
                            for inspector_value in inspector:
                                InspectorValue.objects.update_or_create(url=inspector_value.url,
                                                                        attribute=inspector_value.attribute,
                                                                        value=inspector_value.value,
                                                                        inspector=inspector_value.inspector,
                                                                        runner=inspector_value.runner)
                except Exception as e:
                    print(f"{thread_id} encountered an error:")
                    print(e)
                return
            runner = Runner.objects.get(id=runner_id)
            runner.status = RunnerStatus.RUNNING
            runner.created_at = timezone.now()
            runner.save()

            add_link_to_level(links_queues, Link(start_url))
            level = find_the_links_current_level(links_queues)
            current_active_queue = links_queues[level]
            #  We only stop the thread if one queue is done AND all other threads are also completed
            while len(current_active_queue) != 0 or not all_threads_completed(shared_threads_pool):
                if len(current_active_queue) != 0:
                    print(f"Thread: {thread_id} has queue with links: {len(current_active_queue)}")
                    find_links()
                level = find_the_links_current_level(links_queues)
                if level != -1:
                    current_active_queue = links_queues[level]
                else:
                    print(f"Thread: {thread_id} looking for new queue")
                    shared_threads_pool[thread_id].running = False
                    time.sleep(random.random() * 5)
                    # If all threads are done we break the loop
                    new_queues = split_work_between_threads(shared_threads_pool)
                    if new_queues is not None:
                        shared_threads_pool[thread_id].running = True
                        shared_threads_pool[thread_id].queues = new_queues
                        current_active_queue = next(iter(new_queues.values()))

            driver.quit()
            shared_threads_pool[thread_id].running = False
            print(f"Thread: {thread_id} completed!. Queue: {shared_threads_pool[thread_id]}. Docs: {threads_metrics[thread_id]}")

        # seed_urls = []
        # seed_urls.append(crawler.seed_url)
        # seed_urls.append("https://www.douglas.de/de/c/parfum/damenduefte/koerperpflege/010108")
        # seed_urls.append()
        testing_urls = [
            crawler.seed_url,
            crawler.seed_url,
            crawler.seed_url,
            crawler.seed_url,
        ]
        links[testing_urls[0]] = Link(url=testing_urls[0], visited=False)
        links[testing_urls[1]] = Link(url=testing_urls[1], visited=False)
        links[testing_urls[3]] = Link(url=testing_urls[3], visited=False)
        links[testing_urls[2]] = Link(url=testing_urls[2], visited=False)
        with ThreadPoolExecutor(max_workers=4) as executor:
            crawl_1 = executor.submit(crawl_seed, testing_urls[0])
            crawl_2 = executor.submit(crawl_seed, testing_urls[1])
            # crawl_3 = executor.submit(crawl_seed,testing_urls[2])
            # crawl_4 = executor.submit(crawl_seed, testing_urls[3])

            futures: list[Future] = [crawl_1, crawl_2]
            wait(futures)

        runner = Runner.objects.get(id=runner_id)
        print(f"Docs: {runner.collected_documents}")
        total_visited_links = 0
        total_non_useful_links = 0
        # for key, link in links.items():
        #         if link.visited:
        #             total_visited_links += 1
        #         if not InspectorValue.objects.filter(url=link.url).exists():
        #             print(link.url)
        #             total_non_useful_links += 1

        print(f"Visited Links: {total_visited_links}")
        print(f"total_non_useful_links: {total_non_useful_links}")
        end = time.time()
        print(end - start)
        print(threads_metrics)
        runner.status = RunnerStatus.COMPLETED
        runner.completed_at = timezone.now()
        runner.save()
        logger.info(f"Runner #{runner.id} is completed...")
        logger.info(f"Runner #{runner.id} is completed. Time consumed {end - start}")
        return Response(status=200)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ActionViewSet(EverythingButDestroyViewSet):
    queryset = Action.objects.all().filter(deleted=False)
    serializer_class = ActionPolymorphicSerializer
