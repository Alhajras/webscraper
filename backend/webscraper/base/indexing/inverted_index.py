"""
This class is inspired by the course Information Retrieval by Prof. Dr. Hannah Bast
https://ad-wiki.informatik.uni-freiburg.de/teaching/InformationRetrievalWS2223
"""
import re

from ..models import InspectorValue


class InvertedIndex:
    """
    Class used to create the inverted list of the crawled documents.
    """

    def __init__(self):
        """
        inverted_lists is a map from words that found in the documents to the documents ids.
        """
        self.inverted_lists = {}

    def create_from_runner(self, runner_id: int, included_inspectors_ids: list[int]):
        """
        Generate an inverted index from the given runner.
        :param runner_id: The id of the Runner instance that crawled the documents to be indexed.
        :param included_inspectors_ids: The list which contains the ids of the
        inspectors to be included in the indexing process.
        :return:
        """
        import pdb
        pdb.set_trace()
        # For first stage we want to index by the document title as testing only
        documents = InspectorValue.objects.filter(runner=runner_id).filter(inspector__in=included_inspectors_ids)
        for document in documents:
            # TODO: I think the regular expression for tokenization should be configured by the GUI
            for word in re.split("[^A-Za-z]+", document.value):
                # Neglect capital differences
                word = word.lower()
                # Skip empty spaces
                if len(word) != 0:
                    if not word in self.inverted_lists:
                        self.inverted_lists[word] = []
                    self.inverted_lists[word].append(document.id)
        print(self.inverted_lists)


