"""OpenAI-compatible LLM client.

The project intentionally uses an OpenAI-compatible Chat Completions interface so
it can work with OpenAI and many third-party providers that implement the same
request style, such as DeepSeek, Kimi/Moonshot, Qwen-compatible gateways, etc.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Dict, List

from models import MODULE_TITLES, ProductBrief
from prompt_templates import build_messages


class LLMConfigError(ValueError):
    """Raised when LLM configuration is incomplete."""


class LLMOutputError(ValueError):
    """Raised when model output cannot be parsed into the expected modules."""


@dataclass
class LLMConfig:
    """Configuration for OpenAI-compatible LLM calls."""

    api_key: str
    model: str
    base_url: str = "https://api.openai.com/v1"
    temperature: float = 0.7
    max_tokens: int = 5000


def _extract_json(text: str) -> Dict[str, str]:
    """Extract and parse a JSON object from a model response."""
    cleaned = text.strip()

    # Handle common fenced-code responses even though the prompt forbids them.
    fenced_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, flags=re.DOTALL)
    if fenced_match:
        cleaned = fenced_match.group(1).strip()

    # Handle responses with extra text before/after JSON.
    if not cleaned.startswith("{"):
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            cleaned = cleaned[start : end + 1]

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise LLMOutputError(f"模型返回的内容不是合法 JSON：{exc}") from exc

    if not isinstance(parsed, dict):
        raise LLMOutputError("模型返回的 JSON 不是对象格式。")

    modules: Dict[str, str] = {}
    for title in MODULE_TITLES:
        value = parsed.get(title, "")
        modules[title] = str(value).strip() if value else "待补充：模型未返回此模块。"

    return modules


def generate_workflow_with_llm(brief: ProductBrief, config: LLMConfig) -> Dict[str, str]:
    """Generate the workflow document using an OpenAI-compatible LLM API."""
    if not config.api_key or not config.api_key.strip():
        raise LLMConfigError("缺少 API Key。请在侧边栏填写 API Key，或设置环境变量 LLM_API_KEY / OPENAI_API_KEY。")
    if not config.model or not config.model.strip():
        raise LLMConfigError("缺少模型名称。请在侧边栏填写模型名称，例如 gpt-4o-mini、deepseek-chat 等。")

    try:
        from openai import OpenAI
    except ImportError as exc:
        raise LLMConfigError("未安装 openai 依赖。请运行：python -m pip install -r requirements.txt") from exc

    client_kwargs = {"api_key": config.api_key.strip()}
    if config.base_url and config.base_url.strip():
        client_kwargs["base_url"] = config.base_url.strip().rstrip("/")

    client = OpenAI(**client_kwargs)
    messages: List[Dict[str, str]] = build_messages(brief)

    response = client.chat.completions.create(
        model=config.model.strip(),
        messages=messages,
        temperature=float(config.temperature),
        max_tokens=int(config.max_tokens),
    )

    content = response.choices[0].message.content or ""
    if not content.strip():
        raise LLMOutputError("模型返回为空，请检查模型名称、API Key 或服务商状态。")

    return _extract_json(content)
