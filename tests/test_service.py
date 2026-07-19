import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from zhouli.service import ZhouliConfig, ZhouliService


class FakeProvider:
    def __init__(self, response):
        self.response = response
        self.calls = []

    async def generate(self, **kwargs):
        self.calls.append(kwargs)
        return self.response


class ServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_config_from_mapping_normalizes_provider_and_numeric_bounds(self):
        config = ZhouliConfig.from_mapping(
            {
                "provider_type": " openai_compatible ",
                "api_key": " key ",
                "base_url": " https://api.example.com/v1 ",
                "model": " model-a ",
                "temperature": 0,
                "max_tokens": -1,
                "timeout_seconds": 0,
                "max_input_chars": -300,
            }
        )

        self.assertEqual(config.provider_type, "openai_compatible")
        self.assertEqual(config.api_key, "key")
        self.assertEqual(config.base_url, "https://api.example.com/v1")
        self.assertEqual(config.model, "model-a")
        self.assertEqual(config.temperature, 0)
        self.assertEqual(config.max_tokens, 720)
        self.assertEqual(config.timeout_seconds, 45)
        self.assertEqual(config.max_input_chars, 300)

    async def test_missing_api_key_returns_config_error_before_provider_call(self):
        provider = FakeProvider("不会调用")
        service = ZhouliService({"openai_compatible": provider})
        config = ZhouliConfig(
            provider_type="openai_compatible",
            api_key="",
            base_url="https://api.example.com/v1",
            model="model-a",
        )

        with self.assertRaisesRegex(Exception, "API Key"):
            await service.translate("疯狂星期四", "gentle", "standard", config)

        self.assertEqual(provider.calls, [])

    async def test_translate_builds_prompt_and_cleans_result(self):
        provider = FakeProvider("## 合乎周礼\n**此事可成。**")
        service = ZhouliService({"openai_compatible": provider})
        config = ZhouliConfig(
            provider_type="openai_compatible",
            api_key="unit-test-key",
            base_url="https://api.example.com/v1",
            model="model-a",
        )

        result = await service.translate("疯狂星期四", "gentle", "standard", config)

        self.assertEqual(result, "合乎周礼\n此事可成。")
        call = provider.calls[0]
        self.assertEqual(call["api_key"], "unit-test-key")
        self.assertEqual(call["model"], "model-a")
        self.assertIn("疯狂星期四", call["user_prompt"])


if __name__ == "__main__":
    unittest.main()
