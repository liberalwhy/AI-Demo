"""Shared data models for ecom-content-agent."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


MODULE_TITLES: List[str] = [
    "一、商品信息摘要",
    "二、核心卖点拆解",
    "三、用户痛点与内容切入角度",
    "四、3套短视频内容方案",
    "五、1条完整短视频脚本",
    "六、AI画面/视频Prompt",
    "七、生产SOP",
    "八、质检清单",
    "九、销售/客户FAQ",
    "十、可复用建议",
]


@dataclass
class ProductBrief:
    """Structured product input collected from the Streamlit form."""

    product_name: str
    category: str
    core_selling_points: str
    target_user: str
    platform: str
    content_goal: str
    price_range: str
    use_case: str
    forbidden_claims: str
    reference_style: str
