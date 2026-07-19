# 合乎周礼 AstrBot 适配版

这是 [Aspirin0000/zhouli-translator](https://github.com/Aspirin0000/zhouli-translator) 的 AstrBot 插件适配版，用 `/zhouli` 把现代中文改写成“合乎周礼”的白话翻译腔。

本插件是非官方 AstrBot 适配版。核心创意、提示词风格和 Skill 文案来源于原项目，遵循 MIT License，并保留 `Copyright (c) 2026 Aspirin0000`。

## 用法

```text
/zhouli 疯狂星期四谁请我一食
/周礼 疯狂星期四谁请我一食
/zhouli 小礼 疯狂星期四谁请我一食
/zhouli 强行圆场 小礼 疯狂星期四谁请我一食
/zhouli help
```

## 配置

在 AstrBot WebUI 插件配置中填写：

- `provider_type`：`openai_compatible` 或 `anthropic`
- `api_key`
- `base_url`
- `model`
- `default_mode`
- `default_level`
- `temperature`
- `max_tokens`
- `timeout_seconds`
- `max_input_chars`

插件不使用 AstrBot 全局模型配置。API Key 只从插件配置读取。

## 隐私

插件本身不持久化保存用户输入、生成内容或 API Key。每次使用 `/zhouli` 时，用户输入会发送到你在插件配置中填写的模型服务商；请按所选服务商的隐私政策和数据保留规则评估使用范围。

## 来源

- 原项目：https://github.com/Aspirin0000/zhouli-translator
- 原站：https://hehuzhouli.com
- 许可证：MIT License
