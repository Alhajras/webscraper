import os
import pathlib
import unittest

from backend.webscraper.base.indexing.qgram_index import QGramIndex


class QGramIndexTest(unittest.TestCase):

    def test_normalize(self) -> None:
        q = QGramIndex(3, False)
        result = q.normalize("freiburg")
        expected_result = "freiburg"
        self.assertEqual(result, expected_result)  # add assertion here
        result = q.normalize("Frei, burG !?!")
        expected_result = 'freiburg'
        self.assertEqual(result, expected_result)  # add assertion here

    def test_find_matches(self) -> None:
        pathlib.Path().resolve()
        file_path = os.path.join(
            f"{pathlib.Path().resolve()}/dictionaries/test.tsv")
        q = QGramIndex(3, False)
        q.build_from_file(file_path)
        result = q.find_matches("frei", 0)
        expected_result = ([(1, 0, 3, 1)], 1)
        self.assertEqual(result, expected_result)  # add assertion here
        result = q.find_matches("frei", 2)
        expected_result = ([(1, 0, 3, 1), (2, 1, 2, 2)], 2)
        self.assertEqual(result, expected_result)  # add assertion here
        result = q.find_matches("freibu", 2)
        expected_result = ([(1, 2, 3, 1)], 2)
        self.assertEqual(result, expected_result)  # add assertion here

    def test_merge_lists(self) -> None:
        q = QGramIndex(3, False)
        result = q.merge_lists([[(1, 2), (3, 1), (5, 1)], [(2, 1), (3, 2), (9, 2)]])
        expected_result = [(1, 2), (2, 1), (3, 3), (5, 1), (9, 2)]
        self.assertEqual(result, expected_result)  # add assertion here
        result = q.merge_lists([[(1, 2), (3, 1), (5, 1)], []])
        expected_result = [(1, 2), (3, 1), (5, 1)]
        self.assertEqual(result, expected_result)  # add assertion here
        result = q.merge_lists([[], []])
        expected_result = []
        self.assertEqual(result, expected_result)  # add assertion here

    def test_compute_qgrams(self) -> None:
        q = QGramIndex(3, False)
        self.assertEqual(q.compute_qgrams("freiburg"),
                         ['$$f', '$fr', 'fre', 'rei', 'eib', 'ibu', 'bur', 'urg'])  # add assertion here

    def test_rank_matches(self) -> None:
        q = QGramIndex(3, False)
        result = q.rank_matches([(1, 0, 3, 0), (2, 1, 2, 0), (2, 1, 3, 0), (1, 0, 2, 0)])
        expected_result = [(1, 0, 3, 0), (1, 0, 2, 0), (2, 1, 3, 0), (2, 1, 2, 0)]
        self.assertEqual(result, expected_result)  # add assertion here

    def test_build_from_file(self):
        pathlib.Path().resolve()
        file_path = os.path.join(
            f"{pathlib.Path().resolve()}/dictionaries/test.tsv")

        q = QGramIndex(3, False)
        q.build_from_file(file_path)
        sorted(q.inverted_lists.items())
        expected_value = {
            '$$f': [(1, 1)],
            '$fr': [(1, 1)],
            'fre': [(1, 1)],
            'rei': [(1, 1), (2, 1)],
            '$$b': [(2, 1)],
            '$br': [(2, 1)],
            'bre': [(2, 1)]
        }
        self.assertEqual(q.inverted_lists.items(), expected_value.items())  # add assertion here


if __name__ == '__main__':
    unittest.main()
