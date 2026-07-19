from astrbot.api import AstrBotConfig, logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star

from .zhouli.errors import ZhouliError
from .zhouli.parser import parse_command
from .zhouli.providers import AnthropicProvider, OpenAICompatibleProvider
from .zhouli.service import ZhouliConfig, ZhouliService


HELP_TEXT = """合乎周礼用法：
/zhouli 原话
/周礼 原话
/zhouli 小礼 原话
/zhouli 强行圆场 小礼 原话

辞气：温言相劝 / 大儒辩经 / 强行圆场 / 痛心疾首
篇幅：小礼 / 成礼 / 大礼

请先在插件配置中填写 provider_type、api_key、base_url、model。"""


class ZhouliPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config
        self.service = ZhouliService(
            {
                "openai_compatible": OpenAICompatibleProvider(),
                "anthropic": AnthropicProvider(),
            }
        )

    @filter.command("zhouli", alias={"周礼"})
    async def zhouli(self, event: AstrMessageEvent):
        """把现代中文改写成“合乎周礼”的白话翻译腔。"""
        runtime_config = ZhouliConfig.from_mapping(self.config)
        message = event.get_message_str() if hasattr(event, "get_message_str") else event.message_str
        parsed = parse_command(
            message,
            default_mode=runtime_config.default_mode,
            default_level=runtime_config.default_level,
        )

        if parsed.is_help:
            yield event.plain_result(HELP_TEXT)
            return

        try:
            result = await self.service.translate(
                parsed.text,
                parsed.mode,
                parsed.level,
                runtime_config,
            )
        except ZhouliError as exc:
            yield event.plain_result(str(exc))
            return
        except Exception:
            logger.error("zhouli translate failed unexpectedly")
            yield event.plain_result("礼官远行未归，请稍后再试。")
            return

        yield event.plain_result(result)

    async def terminate(self):
        """AstrBot unload hook."""
