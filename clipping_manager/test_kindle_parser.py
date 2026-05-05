import os

from django.test import TestCase

from clipping_manager.clipping_parser.kindle_clipping_parser import get_clips_from_text


class KindleClippingParserTests(TestCase):

    TEST_FILES = [
        ('myclippings_koreader_lf.txt', 1, 3),
        ('myclippings_kindle_location_lf.txt', 1, 2),
        ('myclippings_mixed_books_lf.txt', 2, 3),
    ]

    def _read_test_data(self, filename):
        test_data_path = os.path.join(os.path.dirname(__file__), 'test_data', filename)
        with open(test_data_path, 'r', encoding='utf-8') as f:
            return f.read()

    def test_parser_matrix(self):
        for filename, expected_books, expected_clippings in self.TEST_FILES:
            with self.subTest(filename=filename):
                content = self._read_test_data(filename)
                clips = get_clips_from_text(content)

                self.assertEqual(len(clips), expected_books)
                self.assertEqual(sum(len(values) for values in clips.values()), expected_clippings)
