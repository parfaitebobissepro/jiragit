import unittest
from src.utils.string_utils import remove_accents

class TestStringUtils(unittest.TestCase):

    def test_remove_accents_valid_cases(self):
        self.assertEqual(remove_accents("café"), "cafe")
        self.assertEqual(remove_accents("résumé"), "resume")
        self.assertEqual(remove_accents("naïve"), "naive")
        self.assertEqual(remove_accents("élève"), "eleve")
        self.assertEqual(remove_accents("coöperate"), "cooperate")

    def test_remove_accents_empty_string(self):
        self.assertEqual(remove_accents(""), "")

    def test_remove_accents_no_accents(self):
        self.assertEqual(remove_accents("hello"), "hello")
        self.assertEqual(remove_accents("world"), "world")

    def test_remove_accents_special_characters(self):
        self.assertEqual(remove_accents("!@#$%^&*()"), "!@#$%^&*()")
        self.assertEqual(remove_accents("1234567890"), "1234567890")

    def test_remove_accents_mixed_characters(self):
        self.assertEqual(remove_accents("héllo wörld!"), "hello world!")
        self.assertEqual(remove_accents("123 café!"), "123 cafe!")

    def test_remove_accents_error_cases(self):
        with self.assertRaises(TypeError):
            remove_accents(None)
        with self.assertRaises(TypeError):
            remove_accents(123)
        with self.assertRaises(TypeError):
            remove_accents(["café"])

if __name__ == "__main__":
    unittest.main()