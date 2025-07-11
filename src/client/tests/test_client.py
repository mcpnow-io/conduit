from unittest import TestCase

from src.client.base import BasePhabricatorClient


class TestBasePhabricatorClient(TestCase):
    def setUp(self):
        super().setUp()

    def test_flatten_params(self):
        with self.subTest("flat_params"):
            flatten = BasePhabricatorClient.flatten_params(
                [{"x": 1, "y": 2}, {"z": 3, "a": 4}]
            )
            self.assertEqual(
                flatten, [("[0][x]", 1), ("[0][y]", 2), ("[1][z]", 3), ("[1][a]", 4)]
            )

        with self.subTest("flat_params_with_prefix"):
            flatten = BasePhabricatorClient.flatten_params(
                [{"x": 1, "y": 2}, {"z": 3, "a": 4}], prefix="test"
            )
            self.assertEqual(
                flatten,
                [
                    ("test[0][x]", 1),
                    ("test[0][y]", 2),
                    ("test[1][z]", 3),
                    ("test[1][a]", 4),
                ],
            )
