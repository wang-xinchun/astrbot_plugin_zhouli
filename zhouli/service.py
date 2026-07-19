from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .core import (
    SYSTEM_PROMPT,
    ConfigError,
    ZhouliLevel,
    ZhouliMode,
    build_user_prompt,
    guarded_result,
    normalize_generated_result,
    require_config_value,
    validate_input,
    validate_level,
    validate_mode,
)


class Provider(Protocol):
    async def generate(self, **kwargs) -> str:
        ...


def _clean_string(value: object, default: str = "") -> str:
    return str(value if value is not None else default).strip()


def _float_in_range(value: object, default: float, minimum: float, maximum: float) -> float:
    if value is None or value == "":
        return default
    try:
        converted = float(value)
    except (TypeError, ValueError):
        return default
    if converted < minimum or converted > maximum:
        return default
    return converted


def _positive_int(value: object, default: int) -> int:
    if value is None or value == "":
        return default
    try:
        converted = int(value)
    except (TypeError, ValueError):
        return default
    if converted <= 0:
        return default
    return converted


@dataclass(frozen=True)
class ZhouliConfig:
    provider_type: str = "openai_compatible"
    api_key: str = ""
    base_url: str = ""
    model: str = ""
    default_mode: ZhouliMode = "gentle"
    default_level: ZhouliLevel = "standard"
    temperature: float = 0.9
    max_tokens: int = 720
    timeout_seconds: int = 45
    max_input_chars: int = 300

    @classmethod
    def from_mapping(cls, data) -> "ZhouliConfig":
        return cls(
            provider_type=_clean_string(data.get("provider_type", "openai_compatible"), "openai_compatible").lower()
            or "openai_compatible",
            api_key=_clean_string(data.get("api_key", "")),
            base_url=_clean_string(data.get("base_url", "")),
            model=_clean_string(data.get("model", "")),
            default_mode=validate_mode(_clean_string(data.get("default_mode", "gentle"), "gentle")),
            default_level=validate_level(_clean_string(data.get("default_level", "standard"), "standard")),
            temperature=_float_in_range(data.get("temperature", 0.9), 0.9, 0, 2),
            max_tokens=_positive_int(data.get("max_tokens", 720), 720),
            timeout_seconds=_positive_int(data.get("timeout_seconds", 45), 45),
            max_input_chars=_positive_int(data.get("max_input_chars", 300), 300),
        )


class ZhouliService:
    def __init__(self, providers: dict[str, Provider]):
        self.providers = providers

    async def translate(
        self,
        text: str,
        mode: ZhouliMode,
        level: ZhouliLevel,
        config: ZhouliConfig,
    ) -> str:
        source_text = validate_input(text, config.max_input_chars)
        mode = validate_mode(mode)
        level = validate_level(level)

        guarded = guarded_result(source_text, level)
        if guarded:
            return guarded

        provider = self.providers.get(config.provider_type)
        if provider is None:
            raise ConfigError("模型接口类型无效，请在插件配置中选择 openai_compatible 或 anthropic。")

        api_key = require_config_value(config.api_key, "请先在插件配置中填写 API Key。")
        base_url = require_config_value(config.base_url, "请先在插件配置中填写 Base URL。")
        model = require_config_value(config.model, "请先在插件配置中填写模型名称。")
        user_prompt = build_user_prompt(source_text, mode, level)

        raw_result = await provider.generate(
            api_key=api_key,
            base_url=base_url,
            model=model,
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            timeout_seconds=config.timeout_seconds,
        )
        return normalize_generated_result(source_text, raw_result, level)
