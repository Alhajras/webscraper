import os
import pathlib
import unittest

from backend.webscraper.base.indexing.qgram_index import QGramIndex


class QGramIndexTest(unittest.TestCase):
    def test_compute_qgrams(self):
        q = QGramIndex(3, False)
        self.assertEqual(q.compute_qgrams("freiburg"), ['$$f', '$fr', 'fre', 'rei', 'eib', 'ibu', 'bur', 'urg'])  # add assertion here

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
