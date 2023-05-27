"""
This class is inspired by the course Information Retrieval by Prof. Dr. Hannah Bast
https://ad-wiki.informatik.uni-freiburg.de/teaching/InformationRetrievalWS2223
"""
import re

from django.core.cache import cache

from ..models import InspectorValue, Inspector, Indexer


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
        cache_key = f"indexer:{indexer_id}"
        hit = cache.get(cache_key)
        if hit is not None:
            print("Cached")
            return hit

        included_inspectors_ids = Inspector.objects.filter(
            indexer=indexer_id
        ).values_list("id", flat=True)
        # For first stage we want to index by the document title as testing only
        documents = InspectorValue.objects.filter(inspector__in=included_inspectors_ids)
        for document in documents:
            # TODO: I think the regular expression for tokenization should be configured by the GUI
            for word in re.split("[^A-Za-z]+", document.value):
                # Neglect capital differences
                word = word.lower()
                # Skip empty spaces
                if len(word) != 0:
                    if word not in self.inverted_lists:
                        self.inverted_lists[word] = []
                    inverted_list_len = len(self.inverted_lists[word])
                    if (
                        inverted_list_len == 0
                        or self.inverted_lists[word][-1] != document.id
                    ):
                        self.inverted_lists[word].append(document.id)
        cache.set(cache_key, self.inverted_lists)

    def cached_indexers_keys(self):
        indexers = Indexer.objects.filter(deleted=False)
        cached_indexers = []
        for indexer in indexers:
            cache_key = f"indexer:{indexer.id}"
            if cache.get(cache_key) is not None:
                cached_indexers.append(indexer)
        return cached_indexers

    def intersect(self, list1, list2):
        """
        Computes the intersection of the two given inverted lists in linear
        time (linear in the total number of elements in the two lists).

        >>> ii = InvertedIndex()
        >>> ii.intersect([1, 5, 7], [2, 4])
        []
        >>> ii.intersect([1, 2, 5, 7], [1, 3, 5, 6, 7, 9])
        [1, 5, 7]
        """
        i = 0  # The pointer in the first list.
        j = 0  # The pointer int the second list.
        result = []

        while i < len(list1) and j < len(list2):
            if list1[i] == list2[j]:
                result.append(list1[i])
                i += 1
                j += 1
            elif list1[i] < list2[j]:
                i += 1
            else:
                j += 1

        return result

    def process_query(self, keywords, indexer_id):
        """
        Processes the given keyword query as follows: Fetches the inverted list
        for each of the keywords in the given query and computes the
        intersection of all inverted lists (which is empty, if there is a
        keyword in the query which has no inverted list in the index).

        >>> ii = InvertedIndex()
        >>> ii.build_from_file("example.tsv")
        >>> ii.process_query([])
        []
        >>> ii.process_query(["doc"])
        [1, 2, 3]
        >>> ii.process_query(["doc", "movie"])
        [1, 3]
        >>> ii.process_query(["doc", "movie", "comedy"])
        []
        """
        if not keywords:
            return []

        cache_key = f"indexer:{indexer_id}"
        self.inverted_lists = cache.get(cache_key)
        if self.inverted_lists is None:
            print(
                f"There is no indexer found with an ID {indexer_id}!"
                f" Please create an indexer first and then try to run queries."
            )
            return []
        # Fetch the inverted lists for each of the given keywords.
        lists = []
        for keyword in keywords:
            if keyword in self.inverted_lists:
                lists.append(self.inverted_lists[keyword])
            else:
                # We can abort, because the intersection is empty
                # (there is no inverted list for the word).
                return []

        # Compute the intersection of all inverted lists.
        if len(lists) == 0:
            return []

        intersected = lists[0]
        for i in range(1, len(lists)):
            intersected = self.intersect(intersected, lists[i])

        return intersected
