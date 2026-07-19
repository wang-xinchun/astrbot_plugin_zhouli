from dataclasses import dataclass

from .core import ZhouliLevel, ZhouliMode


MODE_ALIASES: dict[str, ZhouliMode] = {
    "温言相劝": "gentle",
    "温言": "gentle",
    "劝": "gentle",
    "gentle": "gentle",
    "大儒辩经": "debate",
    "辩经": "debate",
    "大儒": "debate",
    "debate": "debate",
    "强行圆场": "defend",
    "圆场": "defend",
    "洗白": "defend",
    "defend": "defend",
    "痛心疾首": "lament",
    "痛心": "lament",
    "疾首": "lament",
    "lament": "lament",
}

LEVEL_ALIASES: dict[str, ZhouliLevel] = {
    "小礼": "light",
    "短": "light",
    "短一点": "light",
    "短点": "light",
    "短评": "light",
    "一句话": "light",
    "一句评论": "light",
    "light": "light",
    "成礼": "standard",
    "标准": "standard",
    "standard": "standard",
    "大礼": "grand",
    "长": "grand",
    "长一点": "grand",
    "长文": "grand",
    "檄文": "grand",
    "grand": "grand",
}

COMMAND_ALIASES = ("/zhouli", "/周礼", "zhouli", "周礼")
HELP_TOKENS = {"help", "帮助", "-h", "--help", "用法"}


@dataclass(frozen=True)
class ParsedCommand:
    mode: ZhouliMode
    level: ZhouliLevel
    text: str
    is_help: bool = False


def strip_command_prefix(raw: str) -> str:
    value = " ".join(str(raw or "").strip().split())
    for command in COMMAND_ALIASES:
        if value == command:
            return ""
        if value.startswith(f"{command} "):
            return value[len(command) :].strip()
    return value


def parse_command(
    raw: str,
    default_mode: ZhouliMode = "gentle",
    default_level: ZhouliLevel = "standard",
) -> ParsedCommand:
    body = strip_command_prefix(raw)
    if not body or body.lower() in HELP_TOKENS:
        return ParsedCommand(default_mode, default_level, "", True)

    tokens = body.split()
    mode = default_mode
    level = default_level
    consumed: list[int] = []

    for index, token in enumerate(tokens[:4]):
        lowered = token.lower()
        if lowered in MODE_ALIASES:
            mode = MODE_ALIASES[lowered]
            consumed.append(index)
            continue
        if token in MODE_ALIASES:
            mode = MODE_ALIASES[token]
            consumed.append(index)
            continue
        if lowered in LEVEL_ALIASES:
            level = LEVEL_ALIASES[lowered]
            consumed.append(index)
            continue
        if token in LEVEL_ALIASES:
            level = LEVEL_ALIASES[token]
            consumed.append(index)

    remaining = [token for index, token in enumerate(tokens) if index not in consumed]
    return ParsedCommand(mode, level, " ".join(remaining).strip(), False)
