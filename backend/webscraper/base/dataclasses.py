from urllib.parse import urlparse


class CrawlerThread:
    """
    Each crawler is running in an isolated thread, each thread has an id, status and queues of links
    """
    def __init__(self, thread_id: int, running=True, queues={}):
        self.thread_id = thread_id
        self.running = running
        self.queues = queues


class Link:
    """
    Each URL fetched from the web is transformed into Link
    """
    def __init__(self, url: urlparse, visited=False, level=0):
        self.url = url
        self.visited = visited
        self.level = level


class CrawlingLevelsOrder:
    ASC = "ASC"
    DES = "DES"
