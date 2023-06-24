"""
This class is inspired and reuses the code from the course Information Retrieval by Prof. Dr. Hannah Bast
https://ad-wiki.informatik.uni-freiburg.de/teaching/InformationRetrievalWS2223
"""
import re
import math

from django.core.cache import cache

from ..models import InspectorValue, Inspector, Indexer

DEFAULT_B = 0.75
DEFAULT_K = 1.75


class DocumentScore:
    """
    Class that represent the document saved for indexing
    """
    def __init__(self, counter: int, inspector_db_id: int, score: int, document_db_id: int):
        self.counter = counter
        self.inspector_db_id = inspector_db_id
        self.document_db_id = document_db_id
        self.score = score


# class WordsWeight:
#     """
#     Class used to save the words that wanted to be boosted or skipped
#     """
#     def __init__(self, word: str, weight: float):
#         self.word = word
#         self.weight = weight


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

        indexer = Indexer.objects.get(id=indexer_id)

        # Indexer configurations part
        b = indexer.b_parameter
        k = indexer.k_parameter

        # The threshold of which the word is convert to be small and can be neglected
        small_words_threshold = indexer.small_words_threshold

        # Words that should be skipped from indexing
        skip_words_list = indexer.skip_words.split('";"')
        skip_words_dictionary = {value: index for index, value in enumerate(skip_words_list)}

        # TODO: make this configurable
        words_weights = {}
        words_weights["john"] = 0
        words_weights["movies"] = 0

        included_inspectors_ids = Inspector.objects.filter(
            indexer=indexer_id
        ).values_list("id", flat=True)
        # For first stage we want to index by the document title as testing only
        inspector_values = InspectorValue.objects.filter(inspector__in=included_inspectors_ids).order_by("created_at")
        doc_lengths = []
        doc_id = 0
        for inspector_value in inspector_values:
            dl = 0  # Compute the document length (number of words).
            doc_id += 1
            # TODO: I think the regular expression for tokenization should be configured by the GUI
            for word in re.split("[^A-Za-z]+", inspector_value.value):
                # Neglect capital differences
                word = word.lower()

                # Ignore the word if it is empty or small, or it is in the skip list.
                if len(word) <= small_words_threshold or word in skip_words_dictionary:
                    continue

                dl += 1
                # Skip empty spaces
                if word not in self.inverted_lists:
                    # The word is seen for first time, create new list.
                    self.inverted_lists[word] = [
                        DocumentScore(counter=doc_id, inspector_db_id=inspector_value.id, score=1,
                                      document_db_id=inspector_value.document.id)]
                    continue

                # Get last posting to check if the doc was already seen.
                last: DocumentScore = self.inverted_lists[word][-1]
                if last.counter == doc_id:
                    # The doc was already seen, increment tf by 1.
                    self.inverted_lists[word][-1] = DocumentScore(counter=doc_id,
                                                                  inspector_db_id=inspector_value.id,
                                                                  score=last.score + 1,
                                                                  document_db_id=inspector_value.document.id)
                else:
                    # The doc was not already seen, set tf to 1.
                    self.inverted_lists[word].append(
                        DocumentScore(counter=doc_id, inspector_db_id=inspector_value.id, score=1,
                                      document_db_id=inspector_value.document.id))
            # Register the document length.
            doc_lengths.append(dl)

        # Compute N (the total number of documents).
        n = inspector_values.count()
        # Compute AVDL (the average document length).
        avdl = sum(doc_lengths) / n

        # Second pass: Iterate the inverted lists and replace the tf scores by
        # BM25 scores, defined as follows:
        # BM25 = tf * (k + 1) / (k * (1 - b + b * DL / AVDL) + tf) * log2(N/df)
        for word, inverted_list in self.inverted_lists.items():
            for i, document_score in enumerate(inverted_list):
                tf = document_score.score
                doc_id = document_score.counter
                # Obtain the document length (dl) of the document.
                dl = doc_lengths[doc_id - 1]  # doc_id is 1-based.
                # Compute alpha = (1 - b + b * DL / AVDL).
                alpha = 1 - b + (b * dl / avdl)
                # Compute tf2 = tf * (k + 1) / (k * alpha + tf).
                tf2 = tf * (1 + (1 / k)) / (alpha + (tf / k)) if k > 0 else 1
                # Compute df (that is the length of the inverted list).
                df = len(self.inverted_lists[word])
                # Compute the BM25 score = tf' * log2(N/df).
                score = tf2 * math.log(n / df, 2)
                if word in words_weights:
                    score += words_weights[word]
                inverted_list[i] = DocumentScore(counter=doc_id, inspector_db_id=document_score.inspector_db_id,
                                                 score=score,
                                                 document_db_id=document_score.document_db_id)

        cache.set(cache_key, self.inverted_lists)

    def cached_indexers_keys(self):
        indexers = Indexer.objects.filter(deleted=False)
        cached_indexers = []
        for indexer in indexers:
            cache_key = f"indexer:{indexer.id}"
            if cache.get(cache_key) is not None:
                cached_indexers.append(indexer)
        return cached_indexers

    def merge(self, list1: list, list2: list) -> list:
        """
        Compute the union of the two given inverted lists in linear time
        (linear in the total number of entries in the two lists), where the
        entries in the inverted lists are postings of form (doc_id, bm25_score)
        and are expected to be sorted by doc_id, in ascending order.

        >>> ii = InvertedIndex()
        >>> l1 = ii.merge([(1, 2.1), (5, 3.2)], [(1, 1.7), (2, 1.3), (6, 3.3)])
        >>> [(id, "%.1f" % tf) for id, tf in l1]
        [(1, '3.8'), (2, '1.3'), (5, '3.2'), (6, '3.3')]

        >>> l2 = ii.merge([(3, 1.7), (5, 3.2), (7, 4.1)], [(1, 2.3), (5, 1.3)])
        >>> [(id, "%.1f" % tf) for id, tf in l2]
        [(1, '2.3'), (3, '1.7'), (5, '4.5'), (7, '4.1')]

        >>> l2 = ii.merge([], [(1, 2.3), (5, 1.3)])
        >>> [(id, "%.1f" % tf) for id, tf in l2]
        [(1, '2.3'), (5, '1.3')]

        >>> l2 = ii.merge([(1, 2.3)], [])
        >>> [(id, "%.1f" % tf) for id, tf in l2]
        [(1, '2.3')]

        >>> l2 = ii.merge([], [])
        >>> [(id, "%.1f" % tf) for id, tf in l2]
        []
        """
        i = 0  # The pointer in the first list.
        j = 0  # The pointer in the second list.
        result = []

        # Iterate the lists in an interleaving order and aggregate the scores.
        while i < len(list1) and j < len(list2):
            if i < list1[i].counter == list2[j].counter:
                result.append(DocumentScore(counter=list1[i].counter, inspector_db_id=list1[i].inspector_db_id,
                                            score=list1[i].score + list2[j].score,
                                            document_db_id=list1[i].document_db_id))
                i += 1
                j += 1
            elif list1[i].counter < list2[j].counter:
                result.append(list1[i])
                i += 1
            else:
                result.append(list2[j])
                j += 1

        # Append the rest of the first list.
        while i < len(list1):
            result.append(list1[i])
            i += 1

        # Append the rest of the second list.
        while j < len(list2):
            result.append(list2[j])
            j += 1

        return result

    def process_query(self, keywords, indexer_id, use_refinements=False):
        """
        Process the given keyword query as follows: Fetch the inverted list for
        each of the keywords in the query and compute the union of all lists.
        Sort the resulting list by BM25 scores in descending order.

        This method returns _all_ results for the given query, not just the
        top 3!

        If you want to implement some ranking refinements, make these
        refinements optional (their use should be controllable via the
        use_refinements flag).

        >>> ii = InvertedIndex()
        >>> ii.inverted_lists = {
        ... "foo": [(1, 0.2), (3, 0.6)],
        ... "bar": [(1, 0.4), (2, 0.7), (3, 0.5)],
        ... "baz": [(2, 0.1)]}
        >>> result = ii.process_query(["foo", "bar"], use_refinements=False)
        >>> [(id, "%.1f" % tf) for id, tf in result]
        [(3, '1.1'), (2, '0.7'), (1, '0.6')]
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

        # Compute the union of all inverted lists.
        if len(lists) == 0:
            return []

        union = lists[0]
        for i in range(1, len(lists)):
            union = self.merge(union, lists[i])

        # Filter all postings with BM25 = 0.
        union = [x for x in union if x.score != 0]

        # Sort the postings by BM25 scores, in descending order.
        return sorted(union, key=lambda x: x.score, reverse=True)
