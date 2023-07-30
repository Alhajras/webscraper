"""
This class is inspired and reuses the code from the course Information Retrieval by Prof. Dr. Hannah Bast
https://ad-wiki.informatik.uni-freiburg.de/teaching/InformationRetrievalWS2223
"""
import re
import math
from concurrent.futures import ThreadPoolExecutor, Future, wait

from sympy import var, sympify
from .qgram_index import SingletonMeta
from ..models import InspectorValue, Inspector, Indexer

DEFAULT_B = 0.75
DEFAULT_K = 1.75

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
        singleton_cache = SingletonMeta
        cache_key = f"indexer:{indexer_id}"
        hit = singleton_cache.indexers_cache.get(cache_key, None)
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
        skip_words_dictionary = {
            value: index for index, value in enumerate(skip_words_list)
        }

        words_weights = {}
        if indexer.weight_words != '':
            weight_words_list = indexer.weight_words.split('";"')
            for weight in weight_words_list:
                key_value = weight.split("=")
                words_weights[key_value[0]] = int(key_value[1])

        included_inspectors_ids = Inspector.objects.filter(
            indexer=indexer_id
        ).values_list("id", flat=True)
        # For first stage we want to index by the document title as testing only
        inspector_values = InspectorValue.objects.filter(
            inspector__in=included_inspectors_ids
        ).order_by("created_at")
        if len(inspector_values) == 0:
            print("No documents are found to be indexed!")
            return

        # Init all lengths to zero
        doc_lengths = [0] * len(inspector_values)
        def collect_words(inspector_values, doc_id) -> None:
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
                        # counter: int, inspector_db_id: int, score: int, document_db_id: int
                        self.inverted_lists[word] = [(doc_id, inspector_value.id, 1, inspector_value.document.id)]
                        continue

                    # Get last posting to check if the doc was already seen.
                    last = self.inverted_lists[word][-1]
                    if last[0] == doc_id:
                        # The doc was already seen, increment tf by 1.
                        self.inverted_lists[word][-1] = (
                        doc_id, inspector_value.id, last[2] + 1, inspector_value.document.id)
                    else:
                        # The doc was not already seen, set tf to 1.
                        self.inverted_lists[word].append((doc_id, inspector_value.id, 1, inspector_value.document.id))
                # Register the document length.
                doc_lengths[doc_id] = dl

        threads = 2
        # Step 1: Calculate the size of each partition
        partition_size = len(inspector_values) // threads

        # Step 2: Create the partitions
        partitions = [inspector_values[i:i + partition_size] for i in range(0, len(inspector_values), partition_size)]

        with ThreadPoolExecutor(max_workers=threads) as executor:
            thread_1: Future = executor.submit(collect_words, partitions[0], 0)
            thread_2: Future = executor.submit(collect_words, partitions[1], len(partitions[0]) - 1)
            wait([thread_1, thread_2])
        # Compute N (the total number of documents).
        n = inspector_values.count()
        # Compute AVDL (the average document length).
        avdl = sum(doc_lengths) / n

        # Second pass: Iterate the inverted lists and replace the tf scores by
        # BM25 scores, defined as follows:
        # BM25 = tf * (k + 1) / (k * (1 - b + b * DL / AVDL) + tf) * log2(N/df)
        for word, inverted_list in self.inverted_lists.items():
            for i, document_score in enumerate(inverted_list):
                tf = document_score[2]
                doc_id = document_score[0]
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
                inverted_list[i] = (doc_id, document_score[1], score, document_score[3])

        singleton_cache.indexers_cache[cache_key] = self.inverted_lists

    def cached_indexers_keys(self):
        singleton_cache = SingletonMeta

        indexers = Indexer.objects.filter(deleted=False)
        cached_indexers = []
        for indexer in indexers:
            cache_key = f"indexer:{indexer.id}"
            if singleton_cache.indexers_cache.get(cache_key) is not None:
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
                result.append((list1[i].counter,
                               list1[i].inspector_db_id,
                               list1[i].score + list2[j].score,
                               list1[i].document_db_id,))
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

    @staticmethod
    def evaluate_formula(indexer_id: int, variables_names, inspector_values: list) -> int:
        """
        Indexers have the `boosted_formula` field this method will evalute the
        formula output and return the resulting score
        """
        indexer = Indexer.objects.get(pk=indexer_id)
        boosting_formula = indexer.boosting_formula
        # If the formula field is empty we do not continue
        if boosting_formula is None or boosting_formula == '' or len(variables_names) == 0:
            return 0
        res = 0
        try:
            variable_value_map = {}
            for inspector_value in inspector_values:
                variable_name = inspector_value['inspector__variable_name'].strip()
                if variable_name != '':
                    value = inspector_value['value'].strip()
                    # Applying the clean-up expressions
                    for reg_expression in inspector_value['inspector__clean_up_expression'].split('";"'):
                        k, v = reg_expression.split('=')
                        value = re.sub(k, v, value)
                    variable_value_map[variable_name] = float(value)

            from math import log

            expr = sympify(boosting_formula)
            res = expr.subs(variable_value_map.items())
        except Exception as e:
            print(f"Error while evaluating score: {e}")
        return eval(str(res))

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

        singleton_cache = SingletonMeta
        cache_key = f"indexer:{indexer_id}"
        self.inverted_lists = singleton_cache.indexers_cache.get(cache_key, None)
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
        union = [x for x in union if x[3] != 0]
        # Sort the postings by BM25 scores, in descending order.
        return sorted(union, key=lambda x: x[3], reverse=True)
