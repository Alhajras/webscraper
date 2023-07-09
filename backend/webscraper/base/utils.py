import time

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


def extract_disallow_lines_from_url(url):
    """
    Used to extract the Disallow urls from the Robots.txt file
    """
    if url == "" or url is None:
        return []
    disallow_lines = []
    try:
        response = requests.get(url)
        if response.status_code == 200:
            file_content = response.text

            for line in file_content.split("\n"):
                if "Disallow" in line:
                    disallow_lines.append(line.replace("Disallow:", "").strip())

        else:
            print(f"Failed to retrieve file. Status code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {str(e)}")

    return disallow_lines


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
    # TODO Change this to use the template
    # actions_chain = ActionChain.objects.get(template=template)
    actions_chain = ActionChain.objects.all()[0]
    if actions_chain.disabled:
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
                    time.sleep(2)
        except NoSuchElementException:
            print("Action button was not found")
