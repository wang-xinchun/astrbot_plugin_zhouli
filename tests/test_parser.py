import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from zhouli.parser import parse_command


class ParseCommandTests(unittest.TestCase):
    def test_defaults_for_plain_zhouli_command(self):
        parsed = parse_command("/zhouli 疯狂星期四谁请我一食")

        self.assertEqual(parsed.mode, "gentle")
        self.assertEqual(parsed.level, "standard")
        self.assertEqual(parsed.text, "疯狂星期四谁请我一食")
        self.assertFalse(parsed.is_help)

    def test_chinese_alias_command_matches_primary_command(self):
        parsed = parse_command("/周礼 疯狂星期四谁请我一食")

        self.assertEqual(parsed.mode, "gentle")
        self.assertEqual(parsed.level, "standard")
        self.assertEqual(parsed.text, "疯狂星期四谁请我一食")

    def test_extracts_mode_and_level_from_chinese_prefixes(self):
        parsed = parse_command("/zhouli 强行圆场 小礼 疯狂星期四谁请我一食")

        self.assertEqual(parsed.mode, "defend")
        self.assertEqual(parsed.level, "light")
        self.assertEqual(parsed.text, "疯狂星期四谁请我一食")

    def test_extracts_natural_language_length_prefixes(self):
        parsed = parse_command("/zhouli 短一点 疯狂星期四")

        self.assertEqual(parsed.level, "light")
        self.assertEqual(parsed.text, "疯狂星期四")

    def test_extracts_grand_length_prefixes(self):
        parsed = parse_command("/zhouli 檄文 疯狂星期四")

        self.assertEqual(parsed.level, "grand")
        self.assertEqual(parsed.text, "疯狂星期四")

    def test_help_command(self):
        parsed = parse_command("/zhouli help")

        self.assertTrue(parsed.is_help)
        self.assertEqual(parsed.text, "")


if __name__ == "__main__":
    unittest.main()
