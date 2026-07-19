from __future__ import annotations

from collections.abc import Callable
from typing import Any

from ..errors import OutputError, ProviderError


def _join_url(base_url: str, path: str) -> str:
    return f"{base_url.rstrip('/')}/{path.lstrip('/')}"


class AnthropicProvider:
    def __init__(self, client_factory: Callable[[int], Any] | None = None):
        self._client_factory = client_factory

    def _make_client(self, timeout_seconds: int):
        if self._client_factory:
            return self._client_factory(timeout_seconds)
        import httpx

        return httpx.AsyncClient(timeout=timeout_seconds)

    async def generate(
        self,
        *,
        api_key: str,
        base_url: str,
        model: str,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int,
        timeout_seconds: int,
    ) -> str:
        payload = {
            "model": model,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        url = _join_url(base_url, "/v1/messages")

        try:
            async with self._make_client(timeout_seconds) as client:
                response = await client.post(url, headers=headers, json=payload)
        except Exception as exc:
            raise ProviderError("模型服务请求失败，请检查网络、Base URL 或超时时间。") from exc

        if response.status_code in {401, 403}:
            raise ProviderError("模型服务认证失败，请检查 API Key 或模型权限。")
        if response.status_code == 429:
            raise ProviderError("模型服务返回限流，请稍后再试。")
        if response.status_code >= 400:
            raise ProviderError("模型服务暂未回应，请稍后再试。")

        try:
            data = response.json()
            text = "".join(
                item.get("text", "")
                for item in data.get("content", [])
                if item.get("type") == "text"
            )
        except Exception as exc:
            raise OutputError("此言尚未成礼，请再试一次。") from exc

        if not str(text or "").strip():
            raise OutputError("此言尚未成礼，请再试一次。")
        return str(text).strip()

