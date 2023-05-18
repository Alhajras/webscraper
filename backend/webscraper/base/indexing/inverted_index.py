"""
This class is inspired by the course Information Retrieval by Prof. Dr. Hannah Bast
https://ad-wiki.informatik.uni-freiburg.de/teaching/InformationRetrievalWS2223
"""
import re

from django.core.cache import cache

from ..models import InspectorValue, Inspector


class InvertedIndex:
    """
    Class used to create the inverted list of the crawled documents.
    """

    def __init__(self):
        """
        inverted_lists is a map from words that found in the documents to the documents ids.
        """
        self.inverted_lists = {}

    def create_index(self, indexer_id):
        """
        Generate an inverted index from the given runner.
        :param indexer_id: The id of the INdewxer instance that crawled the documents to be indexed.
        :return:
        """
        # The list which contains the ids of the
        #         inspectors to be included in the indexing process.
        cache_key = f'indexer:{indexer_id}'
        hit = cache.get(cache_key)
        if hit is not None:
            print("Cached")
            return hit

        included_inspectors_ids = Inspector.objects.filter(indexer=indexer_id).values_list('id', flat=True)
        import pdb
        pdb.set_trace()
        # For first stage we want to index by the document title as testing only
        documents = InspectorValue.objects.filter(inspector__in=included_inspectors_ids)
        for document in documents:
            # TODO: I think the regular expression for tokenization should be configured by the GUI
            for word in re.split("[^A-Za-z]+", document.value):
                # Neglect capital differences
                word = word.lower()
                # Skip empty spaces
                if len(word) != 0:
                    if not word in self.inverted_lists:
                        self.inverted_lists[word] = []
                    inverted_list_len = len(self.inverted_lists[word])
                    if inverted_list_len == 0 or self.inverted_lists[word][-1] != document.id:
                        self.inverted_lists[word].append(document.id)
        print(self.inverted_lists)
        cache.set(cache_key, self.inverted_lists)



