import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from zhouli.errors import ProviderError
from zhouli.providers.anthropic import AnthropicProvider
from zhouli.providers.openai_compatible import OpenAICompatibleProvider


class FakeResponse:
    def __init__(self, status_code=200, payload=None, text=""):
        self.status_code = status_code
        self._payload = payload or {}
        self.text = text

    def json(self):
        return self._payload


class FakeAsyncClient:
    def __init__(self, response):
        self.response = response
        self.requests = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, url, headers=None, json=None):
        self.requests.append({"url": url, "headers": headers or {}, "json": json or {}})
        return self.response


class ProviderTests(unittest.IsolatedAsyncioTestCase):
    async def test_openai_compatible_request_shape_and_parse(self):
        client = FakeAsyncClient(
            FakeResponse(
                payload={"choices": [{"message": {"content": "合乎周礼"}}]},
            )
        )
        provider = OpenAICompatibleProvider(client_factory=lambda timeout: client)

        result = await provider.generate(
            api_key="unit-test-key",
            base_url="https://api.example.com/v1",
            model="model-a",
            system_prompt="system",
            user_prompt="user",
            temperature=0.9,
            max_tokens=720,
            timeout_seconds=45,
        )

        self.assertEqual(result, "合乎周礼")
        request = client.requests[0]
        self.assertEqual(request["url"], "https://api.example.com/v1/chat/completions")
        self.assertEqual(request["headers"]["Authorization"], "Bearer unit-test-key")
        self.assertEqual(request["json"]["messages"][0], {"role": "system", "content": "system"})
        self.assertEqual(request["json"]["messages"][1], {"role": "user", "content": "user"})
        self.assertFalse(request["json"]["stream"])

    async def test_anthropic_request_shape_and_parse(self):
        client = FakeAsyncClient(
            FakeResponse(
                payload={"content": [{"type": "text", "text": "合乎周礼"}]},
            )
        )
        provider = AnthropicProvider(client_factory=lambda timeout: client)

        result = await provider.generate(
            api_key="unit-test-anthropic-key",
            base_url="https://api.anthropic.com",
            model="claude-test",
            system_prompt="system",
            user_prompt="user",
            temperature=0.9,
            max_tokens=720,
            timeout_seconds=45,
        )

        self.assertEqual(result, "合乎周礼")
        request = client.requests[0]
        self.assertEqual(request["url"], "https://api.anthropic.com/v1/messages")
        self.assertEqual(request["headers"]["x-api-key"], "unit-test-anthropic-key")
        self.assertEqual(request["headers"]["anthropic-version"], "2023-06-01")
        self.assertEqual(request["json"]["system"], "system")
        self.assertEqual(request["json"]["messages"], [{"role": "user", "content": "user"}])

    async def test_provider_auth_error_is_user_facing(self):
        client = FakeAsyncClient(FakeResponse(status_code=401, payload={"error": "bad key"}))
        provider = OpenAICompatibleProvider(client_factory=lambda timeout: client)

        with self.assertRaisesRegex(ProviderError, "API Key"):
            await provider.generate(
                api_key="bad",
                base_url="https://api.example.com/v1",
                model="model-a",
                system_prompt="system",
                user_prompt="user",
                temperature=0.9,
                max_tokens=720,
                timeout_seconds=45,
            )


if __name__ == "__main__":
    unittest.main()
