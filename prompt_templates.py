"""Prompt templates for LLM-powered content workflow generation."""

from __future__ import annotations

from dataclasses import asdict
from typing import Dict, List

from models import MODULE_TITLES, ProductBrief


def build_system_prompt() -> str:
    """Return the system prompt used for e-commerce content workflow generation."""
    modules_text = "\n".join([f"- {title}" for title in MODULE_TITLES])
    return f"""
你是一名资深电商内容策略负责人，同时懂短视频编导、销售转化、AI 画面 Prompt、内容生产 SOP 和平台合规。
你的任务不是写普通文案，而是把用户输入的商品资料，拆解成一份可交付、可培训、可复用的电商内容工作流文档。

你必须输出中文，并严格返回 JSON 对象，不要返回 Markdown 代码块，不要添加 JSON 以外的解释。
JSON 的 key 必须且只能是以下 10 个模块标题：
{modules_text}

每个 value 都是一段 Markdown 文本，可包含表格、标题、清单、脚本分镜、FAQ。输出要像真实业务交付文档，不要像闲聊回答。

质量要求：
1. 结合商品品类、平台、目标用户、使用场景，给出具体内容策略。
2. 脚本要有短视频感：前三秒钩子、痛点场景、产品出场、卖点证明、适合人群、风险边界、行动号召。
3. 不要堆空泛词，如“高端大气”“提升体验”，必须写出用户为什么会在意。
4. 严格遵守用户填写的“禁忌/不能夸大的点”，避免绝对化、医疗化、虚假承诺、竞品贬低。
5. FAQ 要像销售/客服真的能复制使用。
6. SOP 和质检清单要能指导团队协作，而不是泛泛而谈。
7. AI 画面/视频 Prompt 要能直接给 Midjourney、即梦、可灵、Runway、Pika 等视觉工具参考。
8. 不要编造无法验证的数据、认证、销量、获奖信息。
""".strip()


def build_user_prompt(brief: ProductBrief) -> str:
    """Build a structured user prompt from ProductBrief."""
    brief_dict: Dict[str, str] = asdict(brief)
    field_names = {
        "product_name": "商品名称",
        "category": "商品品类",
        "core_selling_points": "核心卖点",
        "target_user": "目标用户",
        "platform": "售卖平台",
        "content_goal": "内容目标",
        "price_range": "价格区间",
        "use_case": "使用场景",
        "forbidden_claims": "禁忌/不能夸大的点",
        "reference_style": "参考风格",
    }
    lines = ["请基于以下商品资料生成完整电商内容工作流文档："]
    for key, label in field_names.items():
        value = brief_dict.get(key, "") or "未填写"
        lines.append(f"{label}：{value}")

    lines.append(
        """
输出格式要求：
- 只返回一个合法 JSON 对象。
- JSON key 必须使用指定的 10 个中文模块标题。
- JSON value 使用 Markdown 字符串。
- 不要输出 ```json 代码块。
- 内容要偏真实业务交付，不要像普通聊天。
""".strip()
    )
    return "\n".join(lines)


def build_messages(brief: ProductBrief) -> List[Dict[str, str]]:
    """Build OpenAI-compatible chat messages."""
    return [
        {"role": "system", "content": build_system_prompt()},
        {"role": "user", "content": build_user_prompt(brief)},
    ]
