class ZhouliError(Exception):
    """Base class for user-facing plugin errors."""


class InputError(ZhouliError):
    """Raised when the command input cannot be translated."""


class ConfigError(ZhouliError):
    """Raised when required plugin configuration is missing or invalid."""


class ProviderError(ZhouliError):
    """Raised when the configured model provider cannot return text."""


class OutputError(ZhouliError):
    """Raised when the provider response contains no usable output."""

