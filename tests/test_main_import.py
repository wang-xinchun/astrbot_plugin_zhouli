import importlib
import sys
import types
import unittest
from pathlib import Path


class MainImportTests(unittest.TestCase):
    def test_main_imports_as_astrbot_package(self):
        plugin_root = Path(__file__).resolve().parents[1]
        plugins_root = plugin_root.parent
        saved_path = list(sys.path)
        saved_modules = dict(sys.modules)

        for name in list(sys.modules):
            if (
                name == "zhouli"
                or name.startswith("zhouli.")
                or name == "astrbot_plugin_zhouli"
                or name.startswith("astrbot_plugin_zhouli.")
                or name == "astrbot"
                or name.startswith("astrbot.")
            ):
                sys.modules.pop(name, None)

        sys.path = [path for path in sys.path if path != str(plugin_root)]
        sys.path.insert(0, str(plugins_root))

        class FakeFilter:
            def command(self, *args, **kwargs):
                def decorator(func):
                    return func

                return decorator

        class FakeStar:
            def __init__(self, context):
                self.context = context

        api = types.ModuleType("astrbot.api")
        api.AstrBotConfig = dict
        api.logger = types.SimpleNamespace(error=lambda *args, **kwargs: None)

        event = types.ModuleType("astrbot.api.event")
        event.AstrMessageEvent = object
        event.filter = FakeFilter()

        star = types.ModuleType("astrbot.api.star")
        star.Context = object
        star.Star = FakeStar

        sys.modules["astrbot"] = types.ModuleType("astrbot")
        sys.modules["astrbot.api"] = api
        sys.modules["astrbot.api.event"] = event
        sys.modules["astrbot.api.star"] = star

        try:
            module = importlib.import_module("astrbot_plugin_zhouli.main")

            self.assertTrue(hasattr(module, "ZhouliPlugin"))
        finally:
            sys.path = saved_path
            sys.modules.clear()
            sys.modules.update(saved_modules)


if __name__ == "__main__":
    unittest.main()
