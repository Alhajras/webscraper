import hashlib
import time
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests
from selenium.common import NoSuchElementException
from selenium.webdriver import Keys
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

from .dataclasses import Link, CrawlerThread
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from .models import (
    Template,
    ActionChain,
    Action,
    ClickAction,
    WaitAction,
    ScrollAction,
    Crawler,
    CrawlingAlgorithms,
)


def fetch_robots_txt(link) -> str:
    """
    Find and parse ROBOTS.txt file
    :param link: Base link that will be used as a source of truth to find the ROBOTS.txt
    :return:
    """
    # Parse the base URL from the provided link
    base_url = urlparse(link)._replace(path="").geturl()

    # Fetch the robots.txt file
    robots_url = base_url + "/robots.txt"
    response = requests.get(robots_url)

    if response.status_code == 200:
        return response.text
    else:
        return None


def check_crawl_permission(robots_txt_content, user_agent, link) -> bool:
    """
    Checks if the crawler allowed to crawl a link
    :param robots_txt_content: ROBOTS.txt file content
    :param user_agent: User used to crawl
    :param link: The link wanted to be crawled
    :return:
    """
    if not robots_txt_content or not link:
        return True
    robot_parser = RobotFileParser()
    robot_parser.parse(robots_txt_content.splitlines())
    robot_parser.set_url(link)  # Set the URL to check permissions

    # Check if the link is allowed to be crawled
    return robot_parser.can_fetch(user_agent, link)


def find_the_links_current_level(
    links_queues: dict[int, list], crawler: Crawler
) -> int:
    """
    We would like to find the queue that contain links left
    :param links_queues: A hashmap with a key of the level and the value is the queue
    :param crawler: Crawler that is in progress.
    :return:
    """
    levels_with_links = []
    for level in links_queues.keys():
        if len(links_queues[level]) > 0:
            levels_with_links.append(level)

    if len(levels_with_links) == 0:
        return -1

    if crawler.parsing_algorithm == CrawlingAlgorithms.BFS_BOTTOM_UP:
        levels_with_links.sort(reverse=True)
    else:
        levels_with_links.sort()
    print(levels_with_links)
    return levels_with_links[0]


def add_link_to_level(links_queues: dict[int, list], link: Link) -> None:
    """
    Helper function used to add links to the corresponding level
    :param links_queues:
    :param link:
    :return:
    """
    if link.level in links_queues.keys():
        links_queues[link.level].append(link)
    else:
        links_queues[link.level] = [link]


def all_threads_completed(shared_threads_pool: dict[int, CrawlerThread]) -> bool:
    """
    Check if all crawlers are completed
    :param shared_threads_pool:
    :return:
    """
    for thread_id, thread in shared_threads_pool.items():
        if thread.running:
            return False
    return True


def split_work_between_threads(
    shared_threads_pool: dict[int, CrawlerThread]
) -> dict[int, list] | None:
    """
    This function will check which threads are not done crawling and will distribute the work between them
    :param shared_threads_pool:
    :return:
    """
    max_length = -1
    max_level = -1
    thread_id_needs_help = -1
    for thread_id, thread in shared_threads_pool.items():
        level = find_the_links_current_level(thread.queues, thread.crawler)
        if level != -1 and len(thread.queues[level]) > max_length:
            max_length = len(thread.queues[level])
            thread_id_needs_help = thread_id
            max_level = level

    long_queue: list = shared_threads_pool[thread_id_needs_help].queues[max_level]
    if len(long_queue) < 5:
        return None
    half_length = len(long_queue) // 2
    shared_threads_pool[thread_id_needs_help].queues[max_level] = long_queue[
        :half_length
    ]
    print(len(long_queue[half_length:]))
    if len(long_queue[half_length:]) == 0:
        return None
    result: dict[int, list] = {max_level: long_queue[half_length:]}
    return result


def create_chrome_driver(show_browser: bool) -> WebDriver:
    """
    Create a new driver to be used for crawling
    :return:chrome driver
    """
    chrome_options = Options()
    user_agent = (
        "Mozilla/5.0 (Windows NT 6.1)"
        " AppleWebKit/537.2 (KHTML, like Gecko) Chrome/110.0.5481.77 Safari/537.2"
    )
    chrome_options.add_argument(f"user-agent={user_agent}")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=2560,1440")
    # Set the implicitly wait time (in seconds)
    if not show_browser:
        chrome_options.add_argument("--headless")  # Hides the browser window
    # Reference the local Chromedriver instance
    chrome_path = r"/usr/bin/chromedriver"
    return webdriver.Chrome(executable_path=chrome_path, options=chrome_options)


def execute_all_before_actions(template: Template, driver: WebDriver) -> None:
    """
    Execute a list of actions to be done before the crawling process,
    some sites needs to accept cookies for example.
    :param template:
    :param driver:
    :return:
    """
    actions_chain = ActionChain.objects.filter(template=template).first()
    if actions_chain == None or actions_chain.disabled:
        return
    all_actions = (
        Action.objects.filter(action_chain=actions_chain)
        .filter(deleted=False)
        .order_by("order")
    )
    for action_to_be_executed in all_actions:
        try:
            if isinstance(action_to_be_executed, ClickAction):
                driver.find_element(By.XPATH, action_to_be_executed.selector).click()
            elif isinstance(action_to_be_executed, WaitAction):
                time.sleep(action_to_be_executed.time)
            elif isinstance(action_to_be_executed, ScrollAction):
                for _ in range(action_to_be_executed.times):
                    body = driver.find_element(By.CSS_SELECTOR, "body")
                    body.send_keys(Keys.SPACE)
                    # We give time for the loading before scrolling again
                    time.sleep(1)
        except NoSuchElementException:
            print("Action button was not found")


def evaluate_document_hash_code(inspector_values: list) -> str:
    input_string = ""
    for value in inspector_values:
        input_string += f"{value.value}{value.attribute}"

    # Generate the SHA1 hash
    sha1_hash = hashlib.sha1(input_string.encode()).hexdigest()
    return sha1_hash
