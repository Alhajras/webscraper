import requests
from django.db import transaction
from urllib.parse import urlparse

from selenium.common import UnexpectedAlertPresentException, WebDriverException

from selenium.webdriver.support.wait import WebDriverWait

from ..models import (
    Runner,
    RunnerStatus,
    Inspector,
    InspectorValue,
    Document,
    LinkFragment,
    Crawler, Statistics
)
import logging
import logging.handlers
from django.utils import timezone
import re
import threading
from concurrent.futures import ThreadPoolExecutor, Future, wait
import time
from selenium.webdriver.common.by import By
from ..dataclasses import Link, CrawlerThread
from ..utils import (
    find_the_links_current_level,
    add_link_to_level,
    split_work_between_threads,
    create_chrome_driver,
    all_threads_completed,
    execute_all_before_actions, fetch_robots_txt, check_crawl_permission, evaluate_document_hash_code,
)


class CrawlerUtils:
    """
    Class to do most of the crawling logic.
    """

    def __init__(self, runner_id: int, crawler_id: int):
        self.runner_id = runner_id
        self.crawler_id = crawler_id

    @staticmethod
    def clean_up_value(value: str, expressions: str) -> str:
        if value == '' or expressions == '':
            return value

        for reg_expression in expressions.split('";"'):
            k, v = reg_expression.split('=')
            value = re.sub(k, v, value)
        return value

    @staticmethod
    def save_url_fragments(url, runner):
        parsed_url = urlparse(url)
        fragments = [parsed_url.netloc] + parsed_url.path.split("/")

        parent = None
        for fragment in fragments:
            if not fragment:
                continue

            try:
                with transaction.atomic():
                    link_fragment = LinkFragment.objects.get(
                        fragment=fragment, parent=parent, runner=runner
                    )
            except Exception:
                link_fragment = LinkFragment(
                    fragment=fragment, parent=parent, runner=runner
                )
                link_fragment.save()

            parent = link_fragment

        return link_fragment

    def create_logger(self) -> logging:
        """
        Creates a logger for the runner to log the history  of the crawler runner.
        :return:
        """
        runner = Runner.objects.get(id=self.runner_id)
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

    def start(self):
        crawler = Crawler.objects.get(pk=self.crawler_id)
        logger = self.create_logger()
        links: dict[str, Link] = {}

        # This dictionary contain all the queues shared between threads
        shared_threads_pool: dict[int, CrawlerThread] = {}
        start = time.time()
        # Define Browser Options
        threads_metrics = {}

        # TODO: Use a better splitter
        # Urls that may crawler navigate by mistake
        excluded_urls = crawler.excluded_urls.split('";"')
        robots_file_link = crawler.robot_file_url if crawler.robot_file_url != '' else crawler.seed_url
        robots_txt_content = fetch_robots_txt(robots_file_link)

        scope_divs = []
        # We read the scopes from the user input if it is not empty otherwise we get all elements from the DOM body
        if crawler.scope_divs != "":
            scope_divs = crawler.scope_divs.split('";"')
        else:
            scope_divs = ["//body"]
        # Stopping options
        max_collected_docs = crawler.max_collected_docs
        max_visited_links = crawler.max_pages
        max_rec_level = crawler.max_depth

        runner = Runner.objects.get(id=self.runner_id)
        # Statistics variables
        statistics = Statistics.objects.create(runner=runner)
        visited_pages = 0
        http_codes = {}

        def crawl_seed(seed: str) -> None:
            """
            This is the starting point where the crawling process start
            :param seed: The root url to start crawling from
            """
            thread_id = threading.get_native_id()
            driver = create_chrome_driver(crawler.show_browser)
            # Set the maximum time to wait (in seconds)
            wait = WebDriverWait(driver, 10)

            # This will hold all the queues for all the links different levels
            links_queues: dict[int, list] = {}
            crawler_thread = CrawlerThread(
                thread_id=thread_id, crawler=crawler, running=True, queues=links_queues
            )

            if thread_id not in shared_threads_pool:
                shared_threads_pool[thread_id] = crawler_thread

            # This is the base URL that the crawler should only crawl from
            base_url = urlparse(seed).hostname
            start_url = seed
            current_active_queue = []

            def find_links() -> None:
                shared_threads_pool[thread_id].running = True
                runner = Runner.objects.get(id=self.runner_id)

                if runner.status == str(RunnerStatus.EXIT):
                    return

                if len(current_active_queue) == 0:
                    return

                # TODO: This should be configurable
                link: Link = current_active_queue.pop()
                link_fragment = self.save_url_fragments(link.url, runner)
                if runner.collected_documents >= max_collected_docs:
                    statistics.http_codes[f"Stopped because reached {max_collected_docs} docs"] = max_collected_docs
                    return
                logger.info(
                    f"Thread: {thread_id} - {link.url} out of {len(current_active_queue)}"
                )
                # Run the Webdriver, save page an quit browser
                # TODO: I should use `retry` here
                if links[link.url].visited:
                    logger.info(f"Thread: {thread_id} - {link.url} already visited.")
                    return
                start_time = time.time()
                driver.get(link.url)
                # wait = WebDriverWait(driver, 10)
                # wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))

                statistics.visited_pages = statistics.visited_pages + 1
                # Calculate the download time
                end_time = time.time()
                download_time = end_time - start_time
                statistics.avg_loading_time = download_time if statistics.avg_loading_time == 0 else (download_time + statistics.avg_loading_time) / 2
                print(statistics.avg_loading_time)
                # Get the page source
                try:
                    page_source = driver.page_source
                    page_size = len(page_source.encode("utf-8")) / 1048576
                    statistics.avg_page_size = page_size if statistics.avg_page_size == 0 else (page_size + statistics.avg_page_size) / 2
                except (UnexpectedAlertPresentException) as e:
                    logger.error(f"The link {link.url} thrown an error: {e}")

                # Calculate the page size in mega-bytes
                print(statistics.avg_page_size)

                # Get the current URL from Selenium
                # Send a separate HTTP request using requests library to retrieve the status code\
                try:
                    current_url = driver.current_url
                    response = requests.get(current_url)
                    status_code = response.status_code
                    print(status_code)
                    if status_code in http_codes:
                        http_codes[status_code] = http_codes[status_code] + 1
                    else:
                        http_codes[status_code] = 1
                        http_codes[status_code] = 1
                    statistics.http_codes = http_codes
                except (WebDriverException, requests.exceptions.ConnectionError, requests.exceptions.TooManyRedirects) as e:
                    logger.error(f"The link {link.url} thrown an error: {e}")
                    return

                links[link.url].visited = True
                # We execute all the 'before actions' before we start crawling
                execute_all_before_actions(crawler.template, driver)
                # This should be configured
                scoped_elements = []
                try:
                    for scope_div in scope_divs:
                        try:
                            scoped_elements += driver.find_elements(By.XPATH, scope_div)
                        except Exception:
                            print(
                                f"Thread id: {crawler_thread.thread_id} had an error, scope not found."
                            )
                            pass
                    # We stop recursion when we reach tha mx level of digging into pages
                    # We add one layer of depth
                    current_rec_level = link.level + 1
                    if current_rec_level <= max_rec_level:
                        for scoped_element in scoped_elements:
                            # We add one level
                            all_links_in_the_page = scoped_element.find_elements(
                                By.CSS_SELECTOR, "a"
                            )
                            for a in all_links_in_the_page:
                                if a.get_attribute("href") is None:
                                    continue
                                # We skip the fragments as they do not add any product, that why we split by #
                                href = a.get_attribute("href").split("#").pop()
                                # Check if the link is allowed to be crawled
                                # if not check_crawl_permission(robots_txt_content, "testing-agent", href):
                                #     statistics.http_codes[f"Disallow link: {href}"] = 1
                                #     continue
                                # Skip unwanted links
                                if href in excluded_urls:
                                    statistics.http_codes[f"Excluded link: {href}"] = 1
                                    continue
                                # Links from outside the main host are skipped
                                if base_url != urlparse(href).hostname:
                                    statistics.http_codes[f"Cross site link: {href}"] = 1
                                    continue
                                if (
                                        link.url != href
                                        and href not in links
                                        and len(links) < max_visited_links
                                ):
                                    found_link = Link(
                                        url=href, visited=False, level=current_rec_level
                                    )
                                    links[href] = found_link
                                    add_link_to_level(links_queues, found_link)
                    else:
                        statistics.http_codes[f"Reached max recursion level reached {max_rec_level}"] = max_rec_level

                    # We start looking up for the elements we would like to collect inside the page/document
                    inspectors_list = Inspector.objects.filter(
                        template=crawler.template, deleted=False
                    )
                    documents_dict = {}
                    for inspector in inspectors_list:
                        inspector_elements = driver.find_elements(
                            By.XPATH, inspector.selector
                        )
                        if len(inspector_elements) == 0:
                            return
                        documents_dict[inspector] = []
                        if not crawler.allow_multi_elements:
                            inspector_elements = [inspector_elements[0]]
                        for inspector_element in inspector_elements:
                            attribute = ""
                            if inspector.attribute != "":
                                attribute = inspector_element.get_attribute(
                                    inspector.attribute
                                )
                                if attribute is None:
                                    attribute = ""
                            if thread_id not in threads_metrics:
                                threads_metrics[thread_id] = 1
                            else:
                                threads_metrics[thread_id] = (
                                        threads_metrics[thread_id] + 1
                                )
                            threads_metrics[thread_id] += 1
                            documents_dict[inspector].append(
                                InspectorValue(
                                    url=link.url,
                                    link_fragment=link_fragment,
                                    attribute=attribute,
                                    value=self.clean_up_value(inspector_element.text, inspector.clean_up_expression),
                                    inspector=inspector,
                                    runner=runner,
                                )
                            )

                    lengths = [len(doc) for doc in documents_dict.values()]
                    if not all(list_size == lengths[0] for list_size in lengths):
                        logger.info(
                            f"Thread: {thread_id} - The URL: {link.url} has different inspectors lists {lengths}."
                        )
                        return
                    documents_number = lengths[0]
                    # We start saving documents
                    for i in range(documents_number):
                        inspector_values = [documents_dict[inspector][i] for inspector in documents_dict.keys()]
                        document_hash_code = evaluate_document_hash_code(inspector_values)
                        if not Document.objects.filter(hash_code=document_hash_code).exists():
                            Document.objects.create(template=crawler.template, hash_code=document_hash_code)
                            doc = Document.objects.last()
                            for inspector_value in inspector_values:
                                InspectorValue.objects.update_or_create(
                                    url=inspector_value.url,
                                    link_fragment=inspector_value.link_fragment,
                                    attribute=inspector_value.attribute,
                                    value=inspector_value.value,
                                    document=doc,
                                    inspector=inspector_value.inspector,
                                    runner=inspector_value.runner,
                                )
                        else:
                            print(f"Found duplicated contents with hashcode: {document_hash_code}")
                    statistics.average_docs_per_page = documents_number if statistics.average_docs_per_page == 0 else (documents_number + statistics.average_docs_per_page) / 2
                    end_time = time.time()
                    average_processing_time = end_time - start_time
                    statistics.average_processing_time = average_processing_time if statistics.average_processing_time == 0 else (average_processing_time + statistics.average_processing_time) / 2
                    print(statistics.avg_loading_time)
                    statistics.save()
                except Exception as e:
                    print(f"{thread_id} encountered an error:")
                    print(e)
                return

            runner = Runner.objects.get(id=self.runner_id)
            runner.status = RunnerStatus.RUNNING
            runner.created_at = timezone.now()
            runner.save()

            add_link_to_level(links_queues, Link(start_url))
            level = find_the_links_current_level(links_queues, crawler)
            current_active_queue = links_queues[level]
            #  We only stop the thread if one queue is done AND all other threads are also completed
            while len(current_active_queue) != 0 or not all_threads_completed(
                    shared_threads_pool
            ):
                if len(current_active_queue) != 0:
                    find_links()
                else:
                    level = find_the_links_current_level(links_queues, crawler)
                    if level != -1:
                        current_active_queue = links_queues[level]
                    else:
                        shared_threads_pool[thread_id].running = False
                        time.sleep(5)
                        # If all threads are done we break the loop
                        new_queues = split_work_between_threads(shared_threads_pool)
                        if new_queues is not None:
                            shared_threads_pool[thread_id].running = True
                            shared_threads_pool[thread_id].queues = new_queues
                            current_active_queue = next(iter(new_queues.values()))

            driver.quit()
            shared_threads_pool[thread_id].running = False
            print(
                f"Thread: {thread_id} completed!."
                f" Queue: {shared_threads_pool[thread_id]}. Docs: {threads_metrics[thread_id]}"
            )

        links[crawler.seed_url] = Link(url=crawler.seed_url, visited=False)
        threads_number = crawler.threads
        with ThreadPoolExecutor(max_workers=threads_number) as executor:
            futures: list[Future] = []
            for _ in range(threads_number):
                futures.append(executor.submit(crawl_seed, crawler.seed_url))
            wait(futures)

        print(f"Docs: {runner.collected_documents}")
        statistics.save()
        print(f"Visited Links: {visited_pages}")

        total_visited_links = 0
        total_non_useful_links = 0
        visitied = []
        visitied_not_saved = []
        not_visited = []
        for key, link in links.items():
            if link.visited:
                visitied.append(key)
            else:
                not_visited.append(key)
            if not InspectorValue.objects.filter(url=link.url).exists():
                visitied_not_saved.append(key)

        print("--------------------- visited -----------------------")
        print(len(visitied))

        print("--------------------- not_visited -----------------------")
        print(len(not_visited))

        print("--------------------- visitied_not_saved -----------------------")
        print(len(visitied_not_saved))
        end = time.time()
        print(end - start)
        print(threads_metrics)
        runner.status = RunnerStatus.COMPLETED
        runner.completed_at = timezone.now()
        runner.save()
        logger.info(f"Runner #{runner.id} is completed...")
        logger.info(f"Runner #{runner.id} is completed. Time consumed {end - start}")
