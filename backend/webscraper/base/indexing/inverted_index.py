"""
This class is inspired by the course Information Retrieval by Prof. Dr. Hannah Bast
https://ad-wiki.informatik.uni-freiburg.de/teaching/InformationRetrievalWS2223
"""

class InvertedIndex:
    """
    Class used to create the inverted list of the crawled documents.
    """

    def __init__(self):
        """
        inverted_lists is a map from words that found in the documents to the documents ids.
        """
        self.inverted_lists = dict[str, list[int]]
    def create_from_runner(self, runner_id):
        """
        Generate an inverted index from the given runner.
        :param runner_id: The id of the Runner instance that crawled the documents to be indexed.
        :return:
        """
        # For first stage we want to index by the document title as testing only
        documents
