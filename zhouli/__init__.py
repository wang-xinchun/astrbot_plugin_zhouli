"""Core package for the AstrBot Zhouli adapter."""

from .core import SYSTEM_PROMPT, build_user_prompt, clean_generated_text
from .service import ZhouliConfig, ZhouliService

__all__ = [
    "SYSTEM_PROMPT",
    "ZhouliConfig",
    "ZhouliService",
    "build_user_prompt",
    "clean_generated_text",
]

