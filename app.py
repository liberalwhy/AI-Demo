"""ecom-content-agent

A Streamlit demo for turning product inputs into an e-commerce content workflow deliverable.

Current version supports two engines:
1. Local template mode: no API key required, always runnable.
2. LLM API mode: OpenAI-compatible API call, suitable for OpenAI / DeepSeek / Kimi / other compatible providers.
"""

from __future__ import annotations

import os
from dataclasses import asdict
from datetime import datetime
from typing import Dict, Optional

import streamlit as st

from llm_client import LLMConfig, LLMConfigError, LLMOutputError, generate_workflow_with_llm
from local_generator import generate_workflow as generate_workflow_local
from local_generator import safe_text
from models import ProductBrief


# =========================
# Document Builder
# =========================

def build_markdown_document(brief: ProductBrief, modules: Dict[str, str], engine_label: str) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    header = (
        f"# {safe_text(brief.product_name, '示例商品')}｜电商内容工作流 Agent Demo\n\n"
        f"生成时间：{now}\n\n"
        f"生成引擎：{engine_label}\n\n"
    )
    body = "\n\n".join([f"## {title}\n\n{content}" for title, content in modules.items()])
    return header + body + "\n"


# =========================
# Streamlit UI Helpers
# =========================

def set_page_style() -> None:
    st.set_page_config(
        page_title="Ecom Content Agent",
        page_icon="🧩",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1180px;
        }
        .hero-card {
            border: 1px solid #E5E7EB;
            border-radius: 18px;
            padding: 28px 30px;
            background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%);
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);
            margin-bottom: 22px;
        }
        .small-muted {
            color: #64748B;
            font-size: 0.95rem;
            line-height: 1.7;
        }
        .section-card {
            border: 1px solid #E5E7EB;
            border-radius: 14px;
            padding: 18px 20px;
            background: #FFFFFF;
            margin-bottom: 16px;
        }
        .metric-card {
            border: 1px solid #E5E7EB;
            border-radius: 14px;
            padding: 16px;
            background: #F8FAFC;
        }
        div.stButton > button:first-child {
            width: 100%;
            border-radius: 10px;
            height: 44px;
            font-weight: 600;
        }
        textarea, input {
            border-radius: 10px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def get_secret_or_env(secret_name: str, env_names: list[str], default: str = "") -> str:
    """Read config from Streamlit secrets first, then environment variables."""
    try:
        value = st.secrets.get(secret_name, "")
        if value:
            return str(value)
    except Exception:
        pass

    for env_name in env_names:
        value = os.getenv(env_name)
        if value:
            return value
    return default


def render_header() -> None:
    st.markdown(
        """
        <div class="hero-card">
            <h1 style="margin-bottom: 8px;">Ecom Content Agent</h1>
            <p class="small-muted">
            一个面向电商运营、内容团队和销售团队的内容工作流 Agent Demo。
            输入商品资料后，系统会自动生成商品卖点拆解、用户痛点、短视频方案、脚本分镜、AI 画面 Prompt、生产 SOP、质检清单和客户 FAQ。
            当前版本支持本地规则模板模式，也支持 OpenAI-compatible 大模型 API 模式。
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> tuple[str, Optional[LLMConfig], bool]:
    st.sidebar.header("生成引擎设置")
    engine = st.sidebar.radio(
        "选择生成方式",
        options=["本地模板模式", "大模型 API 模式"],
        help="本地模板模式不需要联网和 API Key；API 模式会调用你配置的大模型服务。",
    )

    fallback_to_local = True
    config: Optional[LLMConfig] = None

    if engine == "本地模板模式":
        st.sidebar.success("当前不会调用外部 API，适合本地演示和没有 Key 的情况。")
        st.sidebar.caption("脚本质量受模板限制，但稳定、免费、可离线运行。")
        return engine, config, fallback_to_local

    default_api_key = get_secret_or_env("LLM_API_KEY", ["LLM_API_KEY", "OPENAI_API_KEY"])
    default_base_url = get_secret_or_env("LLM_BASE_URL", ["LLM_BASE_URL", "OPENAI_BASE_URL"], "https://api.openai.com/v1")
    default_model = get_secret_or_env("LLM_MODEL", ["LLM_MODEL", "OPENAI_MODEL"], "gpt-4o-mini")

    st.sidebar.info("API 模式使用 OpenAI-compatible Chat Completions 接口。")
    api_key = st.sidebar.text_input("API Key", value=default_api_key, type="password", help="本地测试可直接填；部署时建议放到 Streamlit Secrets。")
    base_url = st.sidebar.text_input("Base URL", value=default_base_url, help="OpenAI 默认：https://api.openai.com/v1；其他服务商填写其兼容地址。")
    model = st.sidebar.text_input("模型名称", value=default_model, help="例如：gpt-4o-mini、deepseek-chat、moonshot-v1-8k 等。")
    temperature = st.sidebar.slider("创意程度 temperature", min_value=0.0, max_value=1.2, value=0.75, step=0.05)
    max_tokens = st.sidebar.slider("最大输出 tokens", min_value=1500, max_value=12000, value=6000, step=500)
    fallback_to_local = st.sidebar.checkbox("API 失败时自动切换到本地模板", value=True)

    with st.sidebar.expander("常见配置示例"):
        st.markdown(
            """
**OpenAI**
- Base URL：`https://api.openai.com/v1`
- Model：按你的账号可用模型填写

**DeepSeek**
- Base URL：`https://api.deepseek.com`
- Model：`deepseek-chat`

**Kimi / Moonshot**
- Base URL：`https://api.moonshot.cn/v1`
- Model：`moonshot-v1-8k`

不同平台模型名和 Base URL 可能会变化，请以对应服务商后台为准。
"""
        )

    config = LLMConfig(
        api_key=api_key,
        base_url=base_url,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return engine, config, fallback_to_local


def render_form() -> ProductBrief | None:
    with st.form("product_brief_form"):
        st.subheader("商品资料输入")
        col1, col2 = st.columns(2)
        with col1:
            product_name = st.text_input("商品名称", placeholder="例如：轻量便携筋膜枪 Pro")
            category = st.text_input("商品品类", placeholder="例如：个护健康 / 运动恢复")
            target_user = st.text_input("目标用户", placeholder="例如：久坐办公人群、健身新手、送礼用户")
            platform = st.text_input("售卖平台", placeholder="例如：抖音 / 小红书 / 淘宝 / 亚马逊")
            price_range = st.text_input("价格区间", placeholder="例如：199-299 元")
        with col2:
            content_goal = st.text_input("内容目标", placeholder="例如：新品种草、提升转化、直播间引流")
            use_case = st.text_input("使用场景", placeholder="例如：下班回家、运动后放松、办公室午休")
            reference_style = st.text_input("参考风格", placeholder="例如：专业测评、真实体验、轻奢简洁")
            forbidden_claims = st.text_area(
                "禁忌/不能夸大的点",
                placeholder="例如：不能承诺治疗颈椎病，不能说100%有效，不能贬低竞品",
                height=92,
            )
        core_selling_points = st.text_area(
            "核心卖点",
            placeholder="例如：轻量便携；多档力度；低噪音；长续航；适合办公和运动后使用",
            height=110,
        )

        submitted = st.form_submit_button("生成内容工作流文档")

    if not submitted:
        return None

    return ProductBrief(
        product_name=product_name,
        category=category,
        core_selling_points=core_selling_points,
        target_user=target_user,
        platform=platform,
        content_goal=content_goal,
        price_range=price_range,
        use_case=use_case,
        forbidden_claims=forbidden_claims,
        reference_style=reference_style,
    )


def render_output(brief: ProductBrief, modules: Dict[str, str], engine_label: str) -> None:
    st.divider()
    st.subheader("生成结果")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<div class='metric-card'><b>交付形态</b><br/>业务工作流文档</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='metric-card'><b>输出模块</b><br/>10 个结构化模块</div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card'><b>当前引擎</b><br/>{engine_label}</div>", unsafe_allow_html=True)

    doc = build_markdown_document(brief, modules, engine_label)
    st.download_button(
        label="下载 Markdown 交付文档",
        data=doc,
        file_name=f"{safe_text(brief.product_name, 'product')}_content_workflow.md",
        mime="text/markdown",
        use_container_width=True,
    )

    tabs = st.tabs(list(modules.keys()))
    for tab, (title, content) in zip(tabs, modules.items()):
        with tab:
            st.markdown("<div class='section-card'>", unsafe_allow_html=True)
            st.markdown(content)
            st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("查看结构化输入数据"):
        st.json(asdict(brief), expanded=False)


def generate_modules(
    brief: ProductBrief,
    engine: str,
    config: Optional[LLMConfig],
    fallback_to_local: bool,
) -> tuple[Dict[str, str], str]:
    """Generate modules using the selected engine."""
    if engine == "本地模板模式":
        return generate_workflow_local(brief), "本地模板模式"

    if config is None:
        raise LLMConfigError("API 配置为空。")

    try:
        with st.spinner("正在调用大模型生成业务文档……"):
            modules = generate_workflow_with_llm(brief, config)
        return modules, f"大模型 API：{config.model}"
    except (LLMConfigError, LLMOutputError, Exception) as exc:
        if not fallback_to_local:
            raise exc
        st.warning(f"API 调用失败，已自动切换到本地模板模式。失败原因：{exc}")
        return generate_workflow_local(brief), "本地模板模式（API 失败后自动兜底）"


# =========================
# Main App
# =========================

def main() -> None:
    set_page_style()
    engine, config, fallback_to_local = render_sidebar()
    render_header()

    st.info("使用方式：填写商品资料，选择生成引擎，点击生成按钮，即可得到一份偏真实业务交付格式的电商内容工作流文档。")

    brief = render_form()
    if brief:
        try:
            modules, engine_label = generate_modules(brief, engine, config, fallback_to_local)
            render_output(brief, modules, engine_label)
        except Exception as exc:
            st.error(f"生成失败：{exc}")
            st.caption("可以先切换到“本地模板模式”确认项目可运行，再检查 API Key、Base URL 和模型名称。")
    else:
        st.markdown(
            """
            ### Demo 输出包括
            - 商品信息摘要、核心卖点拆解、用户痛点与内容切入角度
            - 3 套短视频内容方案、1 条完整短视频脚本、AI 画面/视频 Prompt
            - 生产 SOP、质检清单、销售/客户 FAQ、可复用建议

            ### 两种生成模式
            - **本地模板模式：** 不需要 API Key，稳定免费，适合基础展示。
            - **大模型 API 模式：** 在侧边栏填写 API Key、Base URL 和模型名称后调用模型，脚本和策略质量会更接近真实内容团队交付。
            """
        )


if __name__ == "__main__":
    main()
