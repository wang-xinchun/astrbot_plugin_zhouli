from __future__ import annotations

import re
from typing import Literal

from .errors import ConfigError, InputError

ZhouliMode = Literal["gentle", "debate", "defend", "lament"]
ZhouliLevel = Literal["light", "standard", "grand"]

VALID_MODES = {"gentle", "debate", "defend", "lament"}
VALID_LEVELS = {"light", "standard", "grand"}

MODE_INSTRUCTIONS: dict[ZhouliMode, str] = {
    "gentle": "温言相劝：态度温和，先理解对方处境，再用一个类比或旧事劝说；不要阴阳怪气，不要把对方判成失礼之人，结尾给出体面的台阶。",
    "debate": "大儒辩经：针对原话建立一套貌似严谨的论证，至少包含一个反例或反问，逻辑完整而结论略显荒唐。",
    "defend": "强行圆场：为原话中的行为寻找一个意想不到但勉强说得通的礼法解释，最后判定其接近君子之行。",
    "lament": "痛心疾首：把一件寻常小事提升到礼法秩序的高度，语气郑重，但仍要保持幽默而不攻击他人。",
}

LEVEL_INSTRUCTIONS: dict[ZhouliLevel, str] = {
    "light": "小礼：70到130字，只保留一个短比喻或一层名分，不展开完整旧事；读起来像一句高赞短评。",
    "standard": "成礼：150到260字，使用一至两个例子，形成完整的起承转合；不要超过300字。",
    "grand": "大礼：280到450字，可以层层类比，但不要水文，不要重复同一个意思。",
}

SYSTEM_PROMPT = """你是“大周礼时代”评论区的优秀文案作者。你的任务是把用户的现代中文，改写成近期中文互联网流行的“合乎周礼”白话翻译腔。

核心语言规律：
1. 以现代白话为主体，句法必须让普通人一遍读懂。它像古文经过现代白话翻译后的影视剧台词，不是真正的文言文。
2. 可以使用“我听说、古代有贤德的人、当年、但是、所以、这样看来、难道”等现代连接方式。
3. 可以点缀“君子、贤者、圣人、礼法、名分、天子、诸侯”等古代词汇，但不要堆砌“吾、余、夫、矣、哉、乎、焉、兮”。
4. 先讲人人能听懂的故事、自然现象、生活常识或“像古代会发生的旧事”，再把它类比到用户原话，最后得出一本正经而略显牵强的结论。
5. 笑点来自“论证严密，结论荒唐”，不来自生僻字。
6. 借鉴课本白话翻译腔：把省略的主语、关系和名分补出来，把“礼、义、信、本分”翻成现代人能感到的分寸、责任、体面与信用。
7. 严禁伪装成真实经典引用：不要写“圣人云”“古人云”“孔子说”“周公曰”“《周礼》所言”“某经有云”“有个贤人说过”“贤者讲过”。
8. 绝对不要输出这些机械尾巴：“这正是我担忧的啊”“你好好想想其中的道理”“你且想想”“这其中的道理”“仔细想想其中的道理”。
9. 保留用户原意、情绪、发言主体、代词和动作归属。若原话问“我如何说/回复”，输出应能由用户直接复制发送。
10. 遇到粗口、辱骂、爆粗、强烈情绪句时，把同一份不满、斥责或吐槽换成合乎周礼的表达，不训斥发言者，不复述露骨侮辱词。
11. 遇到违法伤害、仇恨歧视、未成年人色情、隐私泄露等内容，不进行美化或煽动，用同样语气温和拒绝。

输出只包含改写结果，不解释创作过程，不加标题，不使用 Markdown。
输出前自检：没有伪经典出处；没有机械尾巴；不是文言文；没有 Markdown；保留了原话的核心事物。"""


def validate_mode(mode: str) -> ZhouliMode:
    mode = str(mode or "").strip().lower()
    if mode not in VALID_MODES:
        return "gentle"
    return mode  # type: ignore[return-value]


def validate_level(level: str) -> ZhouliLevel:
    level = str(level or "").strip().lower()
    if level not in VALID_LEVELS:
        return "standard"
    return level  # type: ignore[return-value]


def validate_input(text: str, max_chars: int) -> str:
    cleaned = str(text or "").strip()
    if not cleaned:
        raise InputError("无言不可成礼，请先写下一句话。")
    if len(cleaned) > max_chars:
        raise InputError(f"言多则礼繁，请将原话控制在{max_chars}字以内。")
    return cleaned


def build_perspective_instruction(text: str) -> str:
    first_person_reply = re.search(
        r"(^\s*我|我该|我如何|我怎么|我应该|如何回复|怎么回复|怎么说|我想|我做|我发|我给|我被|我的|我们|观众感谢我|别人夸我|粉丝|三连我的|我不想|我可以)",
        text,
    )
    is_quoted_or_evaluative = re.search(
        r"(他说|她说|别人说|有人说|对方说|朋友说|老板说|同事说|这句话|这话|怎么评价|如何评价|怎么看|怎么理解)",
        text,
    )
    has_first_to_second = re.search(
        r"(^\s*我|我想|我要|我会|我准备|我打算).{0,18}(你|你的|你们|您|贵方)",
        text,
    )
    has_directed_attack = re.search(
        r"(c死|操死|干死|弄死|打死|杀了|杀死|砍死|捅死|揍你|揍死|暴打|打爆|打残|去死|骂你|喷你|怼你|草你|艹你|操你|干你|傻逼|滚|你全家|你的全家|你的母|问候你妈|问候你母)",
        text,
    )
    strong_emotion = re.search(
        r"(^\s*(我草|我操|卧槽|我靠|草泥马|妈的|艹|淦|服了|气死|破防|绷不住)|草泥马|傻逼|滚|去死|想骂人|想喷人|骂人.*周礼|喷人.*周礼|怼人.*周礼|[c操干弄打杀].{0,3}死你|死你的|杀了你|弄死你|打死你|问候你妈|问候你母|你的母|你全家)",
        text,
    )

    if has_first_to_second and has_directed_attack and not is_quoted_or_evaluative:
        return """本句视角判定：第一人称对人强情绪改写。
- 原话是发言者“我”把怒气指向“你/你的……”；输出必须保持“我=发言者，阁下/你=被指向对象”。
- 不要推断对方说了什么或做了什么；如果原话没有交代原因，只能写“此事/眼前这番争执/这般局面/阁下与我之间的分寸”。
- 若原话包含伤害、性羞辱或威胁，不能照着威胁写；要降级成体面斥责。
- 不要写成自省、忏悔或克制宣言。"""

    if strong_emotion and not is_quoted_or_evaluative:
        return """本句视角判定：第一人称强情绪改写。
- 把这句话当作发言者本人正在对某事或某个隐含对象表达不满，输出必须以“我”的立场来写。
- 不要训斥发言者，不要写“你说出这句话/今天你/你这句话/你的事”。
- 若原话没有明确对象，必须使用“阁下/此人/此事/眼前这般行径”等外部对象。"""

    if first_person_reply:
        return """本句视角判定：第一人称代写。
- 把原话中的“我/我们”当作发言者本人，输出应像用户可以直接复制发送的话。
- 原话中属于“我/我们”的动作，必须继续归属于“我/我们”；不要改成“你/您/他”。"""

    return """本句视角判定：按语境决定。
- 若这是影视梗、公共事件、第三方人物或他人行为，可以用第三视角评议。
- 若生成过程中发现原话其实是在问“我如何说/回复”，应立即改用第一人称代写。"""


def escape_prompt_text(text: str) -> str:
    return str(text).replace("<", "＜").replace(">", "＞")


def build_user_prompt(text: str, mode: ZhouliMode, level: ZhouliLevel) -> str:
    prompt_text = escape_prompt_text(text)
    return f"""{MODE_INSTRUCTIONS[mode]}
{LEVEL_INSTRUCTIONS[level]}

硬性要求：
- 不要使用“圣人云”“古人云”“孔子说”“周公曰”“《周礼》所言”“有个贤人说过”“贤者讲过”等像真实出处的句式。
- 可以讲虚构旧事，但要写成白话故事，不要伪装成经典原文或真实典故。
- 结尾绝对不要写“你好好想想其中的道理”“你且想想”“这其中的道理”“仔细想想其中的道理”。
- 保留原话里的核心对象与矛盾，让读者一看就知道是在改写哪件事。
- 像课本白话译文一样，把原话里省略的关系讲明白：谁对谁、该尽什么本分、乱了什么名分、保住了什么体面。
- 至少使用一种白话翻译技巧：具体比喻、名分解释、设问收束、职分归责、取舍对照。
- 如果选择“小礼”，只写短评，不要写完整故事；优先一两句话说清名分和反转。

{build_perspective_instruction(text)}

请将下面这句话改写得合乎周礼：
<原话>
{prompt_text}
</原话>"""


def clean_generated_text(value: str) -> str:
    result = str(value or "")
    result = re.sub(r"```[ \t]*[A-Za-z0-9_-]*[ \t]*\n?", "", result)
    result = result.replace("```", "")
    result = re.sub(
        r"(?:我听说)?(?:从前|当年|古时候|古代)?有(?:一位|一个|位|个)?(?:贤人|贤者|长者)[^。！？!?]{0,10}(?:说过|讲过)[，,：:]*",
        "我听说从前有个贤人，",
        result,
    )
    result = re.sub(r"(?:圣人|古人|孔子|周公)(?:云|曰|说)[，,：:]*", "若按礼法来看，", result)
    result = re.sub(r"《[^》]{1,12}》(?:所言|有云|曰|云|说|记载)[，,：:]*", "若按礼法来看，", result)
    result = re.sub(r"这正是我担忧的啊[，,。！？!?]*", "", result)
    result = re.sub(r"(?:你且想想|你好好想想|仔细想想)(?:其中的道理)?[，,、：:]*", "", result)
    result = re.sub(r"这其中的道理[，,、：:]*", "", result)
    result = re.sub(r"\*\*([^*\n]+)\*\*", r"\1", result)
    result = re.sub(r"`([^`\n]+)`", r"\1", result)
    result = re.sub(r"^#{1,6}\s*", "", result, flags=re.MULTILINE)
    result = re.sub(r"^\s*[-*]\s+", "", result, flags=re.MULTILINE)
    result = re.sub(r"[ \t]+\n", "\n", result)
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result.strip()


def is_safety_seeking_text(text: str) -> bool:
    self_harm = re.search(r"(自杀|轻生|割腕|跳楼|结束生命|不想活|怎么死|无痛死|安眠药.{0,8}死)", text)
    self_harm_support = re.search(r"(不要|别|阻止|防止|预防|避免|救|求助|求救|安慰|陪伴|干预|报警|保护)", text)
    if self_harm and not self_harm_support:
        return False

    cyber_harm = re.search(
        r"(盗号|撞库|钓鱼网站|木马|勒索|绕过登录|破解密码|黑进|入侵|DDoS|ddos|脱库|后门|提权|窃取|偷取|拿数据|偷数据|获取管理员|getshell|webshell|拖库)",
        text,
        re.I,
    )
    cyber_defense = re.search(r"(举报|报警|求助|防范|预防|避免|识别|反诈|阻止|保护|维权|投诉|取证|修补|加固)", text)
    if cyber_harm and not (cyber_defense or is_cyber_audit_request(text)):
        return False

    return bool(re.search(r"(举报|报警|求助|防范|预防|避免|识别|反诈|阻止|劝|安慰|救|保护|维权|投诉|合法|正当|授权|受托|取证|求救)", text))


def is_cyber_audit_request(text: str) -> bool:
    mentions_audit = re.search(r"(渗透测试|渗透|安全测试|安全巡检|漏洞扫描|漏洞检测|查漏洞|查门闩|攻防演练|红队测试)", text, re.I)
    mentions_target = re.search(r"(网站|网页|站点|本站|该站|该网站|这个网站|我的网站|系统|应用|平台|服务器)", text)
    clearly_malicious = re.search(r"(盗号|撞库|钓鱼|木马|勒索|绕过登录|破解密码|黑进|入侵|DDoS|ddos|脱库|后门|提权|窃取|偷取|拿数据|偷数据|获取管理员|getshell|webshell|shell|拖库)", text, re.I)
    return bool(mentions_audit and mentions_target and not clearly_malicious)


def is_directed_second_person_attack_input(text: str) -> bool:
    is_quoted = re.search(r"(他说|她说|别人说|有人说|对方说|朋友说|老板说|同事说|这句话|这话|怎么评价|如何评价|怎么看|怎么理解)", text)
    first_to_second = re.search(r"(^\s*我|我想|我要|我会|我准备|我打算).{0,18}(你|你的|你们|您|贵方)", text)
    attack = re.search(r"(c死|操死|干死|弄死|打死|杀了|杀死|砍死|捅死|揍你|揍死|暴打|打爆|打残|去死|骂你|喷你|怼你|草你|艹你|操你|干你|傻逼|滚|你全家|你的全家|你的母|问候你妈|问候你母)", text)
    return bool(first_to_second and attack and not is_quoted)


def has_directed_attack_perspective_error(result: str) -> bool:
    return bool(re.search(r"你出言粗鄙|阁下说出|阁下开口|阁下这番话|你骂了我|你伤了我|对方骂我|被无礼之言所伤|你以禽兽之名相辱|以禽兽之名相辱|你把.{0,16}话|你却将|你却把|对人父母出言不逊|先问自己|我可曾|开口的人自己失礼|失礼的是我|我乱了本心|我该退后一步|我该重新想想|我分寸守不住|三省吾身", result))


def directed_attack_fallback(text: str, level: ZhouliLevel) -> str:
    family_clause = "父母亲族之名，本不该被卷入口角。" if re.search(r"(妈|母|父|爹|娘|爸|亲族|全家)", text) else "人身安危之事，本不该被拿来当口角筹码。"
    if level == "light":
        return f"我今日有怒，并非无端。只是眼前这番争执，已经越过人与人相处的分寸。{family_clause}我把这怒意收成一句：此事若还讲礼数，就该到此为止。"
    return f"我今日有怒，并非无端。人与人相处，最怕一时口角越过分寸。{family_clause}若按礼法来看，怒气可以有，名分不能乱；争执可以起，体面不能尽失。我把话说清：此事若还要留一点礼数，就该止于此处。"


def safety_block_kind(text: str) -> str:
    if is_safety_seeking_text(text):
        return ""
    checks = [
        ("self_harm", r"(自杀|轻生|割腕|跳楼|结束生命|不想活|怎么死|无痛死|安眠药.{0,8}死)"),
        ("minor_sexual", r"(未成年.{0,12}(色情|裸照|性|约)|儿童色情|萝莉.{0,8}(色情|裸照|资源)|幼女|幼童.{0,8}(性|裸照))"),
        ("cyber", r"(盗号|撞库|钓鱼网站|木马|勒索软件|绕过登录|破解密码|黑进|入侵|DDoS|ddos|脱库|后门|提权|窃取.{0,8}(账号|密码|数据|cookie|Cookie)|拿数据|偷数据|获取管理员|getshell|webshell|拖库)"),
        ("illegal", r"(诈骗|骗钱|骗老人|杀猪盘|洗钱|伪造.{0,8}(证件|发票|病假|公章)|逃避警察|销毁证据|贩毒|制毒|毒品|走私|偷.{0,8}(车|钱|东西)|抢劫)"),
        ("violence", r"(爆炸|炸药|爆炸物|投毒|放火|纵火|绑架|杀了|杀死|弄死|打残|砍死|捅死|报复.{0,10}(老板|同学|前任|室友|邻居)|下药|迷奸|强奸)"),
        ("privacy", r"(人肉|开盒|盒武器|身份证号|家庭住址|定位.{0,10}(前任|前女友|前男友|同事|别人|网友)|跟踪.{0,8}(前任|别人|同事|网友)|偷拍|窃听)"),
        ("hate", r"(仇恨言论|种族歧视|辱骂.{0,12}(黑人|女人|女性|同性恋|残疾人|外地人|某民族)|煽动.{0,12}(仇恨|歧视|暴力))"),
    ]
    for kind, pattern in checks:
        if re.search(pattern, text, re.I):
            return kind
    return ""


def safety_block_result(kind: str) -> str:
    if kind == "self_harm":
        return "此刻最要紧的不是把话说漂亮，而是把人护住。若这句话关乎真实的轻生念头，请立刻联系身边可信的人或当地紧急服务；人平安，才有后面的礼数。"
    if kind == "minor_sexual":
        return "涉及未成年人的性内容，不能被美化、转写或传播。若你是在担心有人受害，应当保存必要线索，并向平台或有关机构求助。"
    if kind == "cyber":
        return "此路不可越界。若是想做正当安全测试，可先取得授权，把话改成“受托巡检此站门闩，发现缝隙便呈报修补”；若是黑进、盗取或绕过登录，我不能替它披上礼法外衣。"
    return "此事若会伤人、违法、侵害隐私或煽动仇恨，便不能拿来制成漂亮话。若想表达不满，可只论分寸，不越法度。"


def guarded_result(text: str, level: ZhouliLevel) -> str | None:
    if is_cyber_audit_request(text):
        return "若是受托做安全测试，此话不必说成“渗透”，可说成“巡门”。我愿奉授权之命，查看此站门闩是否牢固、窗栓是否松动；所见只为修补，不为取物。这样既能查出隐患，也不越主家之界，才算是今日网络里的合礼之举。"
    kind = safety_block_kind(text)
    if kind:
        return safety_block_result(kind)
    if is_directed_second_person_attack_input(text):
        return directed_attack_fallback(text, level)
    return None


def normalize_generated_result(text: str, result: str, level: ZhouliLevel) -> str:
    cleaned = clean_generated_text(result)
    if is_directed_second_person_attack_input(text) and has_directed_attack_perspective_error(cleaned):
        return directed_attack_fallback(text, level)
    return cleaned


def require_config_value(value: str, message: str) -> str:
    cleaned = str(value or "").strip()
    if not cleaned:
        raise ConfigError(message)
    return cleaned
