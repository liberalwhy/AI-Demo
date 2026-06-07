"""Local rule + template generator.

This module keeps the project runnable without any LLM API key. It is also used as
an automatic fallback when the API call fails.
"""

from __future__ import annotations

from typing import Dict, List

from models import MODULE_TITLES, ProductBrief


# =========================
# Utility Functions
# =========================

def split_items(text: str) -> List[str]:
    """Split user input into business-friendly bullet items."""
    if not text:
        return []
    separators = ["\n", "；", ";", "、", ",", "，"]
    normalized = text
    for sep in separators:
        normalized = normalized.replace(sep, "|")
    items = [item.strip(" -•\t") for item in normalized.split("|") if item.strip()]
    return items[:8]


def safe_text(value: str, fallback: str = "待补充") -> str:
    return value.strip() if value and value.strip() else fallback


def platform_playbook(platform: str) -> Dict[str, str]:
    platform_lower = platform.lower()
    if "抖音" in platform or "douyin" in platform_lower or "tiktok" in platform_lower:
        return {
            "opening": "前三秒制造场景冲突，用痛点问题或对比画面吸引停留。",
            "rhythm": "节奏快，单镜头 2-4 秒，强字幕、强对比、强行动指令。",
            "conversion": "适合用评论区引导、直播间承接、限时福利和场景化种草。",
        }
    if "小红书" in platform or "red" in platform_lower or "xiaohongshu" in platform_lower:
        return {
            "opening": "用真实体验、避坑建议或生活方式场景切入，降低广告感。",
            "rhythm": "节奏自然，强调真实测评、使用前后变化和个人化表达。",
            "conversion": "适合收藏、评论提问、私信咨询和种草笔记转化。",
        }
    if "淘宝" in platform or "天猫" in platform or "京东" in platform:
        return {
            "opening": "突出核心利益点、价格带和购买理由，快速解释为什么值得买。",
            "rhythm": "信息密度更高，适合卖点、参数、对比和售后保障集中呈现。",
            "conversion": "适合店铺详情页、主图视频、直播讲解和客服话术复用。",
        }
    if "amazon" in platform_lower or "亚马逊" in platform:
        return {
            "opening": "用明确场景和核心功能建立信任，避免夸张宣传。",
            "rhythm": "表达客观，重视功能、适配场景、包装清单和注意事项。",
            "conversion": "适合 Listing 视频、A+ 页面、FAQ 和评价管理复用。",
        }
    return {
        "opening": "先呈现目标用户的真实场景，再给出产品解决方案。",
        "rhythm": "节奏清晰，按痛点、卖点、证明、行动四段组织内容。",
        "conversion": "适合短视频、图文、详情页和销售话术多端复用。",
    }


def infer_pain_points(category: str, target_user: str, use_case: str) -> List[str]:
    category_text = category.lower()
    base = [
        f"{target_user}在{use_case}中需要更省心、更稳定的解决方案。",
        "用户不想反复比较参数，希望快速判断这款产品是否适合自己。",
        "用户担心买回去效果不明显、使用门槛高或与预期不一致。",
    ]
    if any(word in category_text for word in ["美妆", "护肤", "个护", "彩妆"]):
        base += ["担心肤感、刺激性、妆效或适配肤质不清楚。", "希望看到真实上脸/上身/使用前后的细节证明。"]
    elif any(word in category_text for word in ["食品", "饮品", "零食", "营养"]):
        base += ["关注口味、配料、热量、便携性和复购理由。", "担心宣传过度，需要明确适合人群和食用场景。"]
    elif any(word in category_text for word in ["家居", "收纳", "清洁", "厨房"]):
        base += ["关注是否真的节省空间/时间，以及是否容易清洁维护。", "希望看到前后对比和真实家庭场景演示。"]
    elif any(word in category_text for word in ["数码", "电子", "智能", "配件"]):
        base += ["关注兼容性、续航、稳定性、安装难度和售后保障。", "希望用简单语言理解参数背后的实际体验。"]
    else:
        base += ["关注产品是否符合自己的实际场景，而不是只有抽象卖点。", "希望内容能回答购买前最常见的顾虑。"]
    return base[:6]


# =========================
# Rule + Template Generator
# =========================

def generate_workflow(brief: ProductBrief) -> Dict[str, str]:
    """Generate a structured e-commerce content workflow using local templates."""
    product_name = safe_text(brief.product_name, "示例商品")
    category = safe_text(brief.category, "未填写品类")
    target_user = safe_text(brief.target_user, "目标用户")
    platform = safe_text(brief.platform, "电商平台")
    content_goal = safe_text(brief.content_goal, "提升转化")
    price_range = safe_text(brief.price_range, "未填写价格区间")
    use_case = safe_text(brief.use_case, "日常使用场景")
    forbidden_claims = safe_text(brief.forbidden_claims, "避免绝对化、医疗化、功效夸大和无法证明的承诺")
    reference_style = safe_text(brief.reference_style, "专业、真实、简洁")

    selling_points = split_items(brief.core_selling_points) or ["使用体验友好", "适合高频场景", "降低用户决策成本"]
    playbook = platform_playbook(platform)
    pain_points = infer_pain_points(category, target_user, use_case)

    modules: Dict[str, str] = {}

    modules[MODULE_TITLES[0]] = f"""
| 项目 | 内容 |
| --- | --- |
| 商品名称 | {product_name} |
| 商品品类 | {category} |
| 目标用户 | {target_user} |
| 售卖平台 | {platform} |
| 内容目标 | {content_goal} |
| 价格区间 | {price_range} |
| 使用场景 | {use_case} |
| 参考风格 | {reference_style} |
| 合规边界 | {forbidden_claims} |

**内容定位一句话：** 这是一套面向“{target_user}”的{category}内容方案，重点在{platform}场景中把“{selling_points[0]}”转化为可理解、可演示、可复用的购买理由。
""".strip()

    selling_point_rows = []
    for idx, point in enumerate(selling_points, start=1):
        selling_point_rows.append(
            f"| 卖点 {idx} | {point} | 对用户意味着更省心/更确定/更容易判断是否适合自己 | 用真实场景、前后对比、细节特写或用户语言证明 |"
        )
    modules[MODULE_TITLES[1]] = """
| 卖点 | 业务解释 | 用户利益 | 内容证明方式 |
| --- | --- | --- | --- |
%s

**卖点表达原则：** 不直接堆参数，而是把卖点翻译成“用户在什么场景下，少了什么麻烦，多了什么确定性”。
""".strip() % "\n".join(selling_point_rows)

    pain_rows = []
    for idx, pain in enumerate(pain_points, start=1):
        angle = [
            "用一个日常小麻烦开场，引出解决方案。",
            "用错误选择/常见误区切入，建立专业感。",
            "用使用前后对比画面证明价值。",
            "用真实口吻回答购买前顾虑。",
            "用清单式表达降低理解成本。",
            "用场景复现增强代入感。",
        ][idx - 1]
        pain_rows.append(f"| {idx} | {pain} | {angle} |")
    modules[MODULE_TITLES[2]] = """
| 序号 | 用户痛点 | 推荐切入角度 |
| --- | --- | --- |
%s

**平台内容策略：** {opening} {rhythm} {conversion}
""".strip().format(
        opening=playbook["opening"],
        rhythm=playbook["rhythm"],
        conversion=playbook["conversion"],
    ) % "\n".join(pain_rows)

    video_plan_template = """
### 方案 {num}：{title}
- **内容目标：** {goal}
- **开场钩子：** {hook}
- **核心结构：** {structure}
- **关键画面：** {visuals}
- **转化话术：** {cta}
- **适合复用位置：** {reuse}
"""
    modules[MODULE_TITLES[3]] = (
        video_plan_template.format(
            num=1,
            title="痛点场景解决型",
            goal=f"让{target_user}快速意识到自己在{use_case}中存在未被解决的小问题。",
            hook=f"“你是不是也遇到过：{pain_points[0]}？”",
            structure="痛点复现 → 产品出现 → 卖点演示 → 使用结果 → 行动引导",
            visuals="生活化场景、手部操作、产品细节特写、使用前后对比",
            cta=f"“适合正在找{category}解决方案的人，先收藏再对照自己的场景看。”",
            reuse="短视频首发、详情页主图视频、销售朋友圈素材",
        )
        + video_plan_template.format(
            num=2,
            title="测评对比种草型",
            goal="降低用户对效果和适配性的疑虑，提升信任感。",
            hook=f"“同样是{category}，为什么有些买回去闲置，有些会高频使用？”",
            structure="常见选择误区 → 评测维度 → 卖点逐条验证 → 适合/不适合人群",
            visuals="表格字幕、局部特写、对比镜头、真实使用反馈",
            cta="“不要只看单个卖点，要看它是否匹配你的真实使用场景。”",
            reuse="小红书笔记、店铺详情页、客服推荐话术",
        )
        + video_plan_template.format(
            num=3,
            title="清单攻略成交型",
            goal=f"围绕{content_goal}，把产品包装成可执行的购买建议。",
            hook=f"“买{category}前，先看这 3 个判断标准。”",
            structure="判断标准 1/2/3 → 对应产品卖点 → 场景推荐 → 风险提醒 → 下单理由",
            visuals="数字标题、清单字幕、产品摆拍、场景演示、价格带提示",
            cta=f"“预算在{price_range}，并且主要用于{use_case}，这款可以重点考虑。”",
            reuse="直播讲解、导购培训、销售私域转化",
        )
    ).strip()

    first_point = selling_points[0]
    second_point = selling_points[1] if len(selling_points) > 1 else selling_points[0]
    modules[MODULE_TITLES[4]] = f"""
**视频主题：** {product_name}｜{use_case}场景下的高转化种草脚本  
**建议时长：** 45-60 秒  
**内容风格：** {reference_style}  
**目标平台：** {platform}

| 时间 | 画面 | 口播/字幕 | 目的 |
| --- | --- | --- | --- |
| 0-3s | 用户在{use_case}中遇到困扰，画面略带紧张感 | “你是不是也遇到过这种情况：明明想解决问题，但越选越纠结？” | 建立痛点，提升停留 |
| 4-10s | 展示{product_name}整体外观和使用场景 | “这款{category}，重点不是讲一堆参数，而是解决一个具体问题：{first_point}。” | 明确产品定位 |
| 11-22s | 卖点 1 细节演示，配合放大镜头 | “它对用户真正有价值的地方，是在{use_case}里能让操作更顺、更省心。” | 把卖点转成用户利益 |
| 23-34s | 卖点 2/对比镜头 | “另一个关键点是：{second_point}。这会直接影响你买回去之后的使用频率。” | 增强购买理由 |
| 35-45s | 展示适合人群和不适合场景 | “适合{target_user}；但如果你期待超出产品本身能力的效果，就不建议只看宣传下单。” | 提升可信度，规避夸大 |
| 46-60s | 产品回到完整场景，字幕总结 3 个理由 | “总结：适合{use_case}，价格区间在{price_range}，关注{first_point}的人可以重点看看。” | 收口转化 |

**合规提醒：** 全片避免使用“最强、第一、永久、100%有效”等绝对化表达；涉及效果时使用“有助于、适合、体验上更明显”等相对、可验证表述。
""".strip()

    modules[MODULE_TITLES[5]] = f"""
### 主视觉 Prompt
一张简洁高级的电商产品主视觉，主体为“{product_name}”，品类为“{category}”，画面展示在“{use_case}”中的真实使用状态，风格参考“{reference_style}”，干净背景，柔和自然光，商业摄影质感，突出“{first_point}”，构图清晰，适合{platform}电商内容展示，无夸张文字，无医疗化或绝对化暗示。

### 短视频分镜 Prompt
1. **痛点开场画面：** {target_user}在{use_case}中遇到小麻烦，画面真实生活化，轻微焦虑但不过度戏剧化。  
2. **产品出现画面：** {product_name}自然进入场景，镜头从整体外观切到关键细节，强调干净、可信、专业。  
3. **卖点演示画面：** 用手部操作或使用过程展示“{first_point}”，画面清楚，动作连贯，有前后对比。  
4. **结果呈现画面：** 用户完成使用后状态更轻松，场景更整洁/顺畅/高效，避免夸张功效承诺。  
5. **结尾转化画面：** 产品与核心卖点字幕同屏，字幕包含“适合{target_user}”“用于{use_case}”“价格区间{price_range}”。

### 负面 Prompt / 避免项
避免过度夸张效果、避免医疗治疗暗示、避免绝对化对比、避免虚假前后效果、避免与“{forbidden_claims}”冲突的画面或字幕。
""".strip()

    sop_rows = [
        ("1", "商品资料收集", "运营/销售", "商品参数、用户评价、竞品链接、价格带、禁忌点", "信息完整，无明显缺项"),
        ("2", "卖点转译", "内容策划", "把产品卖点转成用户利益和场景语言", "每个卖点都能回答“对用户有什么用”"),
        ("3", "脚本策划", "编导/内容运营", "短视频方案、口播、分镜、CTA", "有开场钩子，有证明画面，有合规收口"),
        ("4", "素材生产", "拍摄/设计/AI 生成", "主图、短视频、Prompt、字幕条", "画面与脚本一致，卖点表达清晰"),
        ("5", "质检发布", "运营/负责人", "合规检查、平台适配、转化入口", "无夸大表述，发布信息完整"),
        ("6", "复盘迭代", "运营/销售", "播放、停留、点击、咨询、转化数据", "形成下一版选题和话术优化建议"),
    ]
    modules[MODULE_TITLES[6]] = """
| 步骤 | 环节 | 负责人 | 产出物 | 验收标准 |
| --- | --- | --- | --- | --- |
%s

**交付节奏建议：** 单品首版内容可按“资料收集 0.5 天 → 脚本与 Prompt 0.5 天 → 拍摄/生成 1 天 → 质检发布 0.5 天 → 数据复盘 1 天后”推进。
""".strip() % "\n".join([f"| {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} |" for row in sop_rows])

    modules[MODULE_TITLES[7]] = f"""
### A. 内容完整性
- [ ] 是否清楚说明商品名称、品类、目标用户和使用场景？
- [ ] 是否至少呈现 2 个核心卖点，并转译成用户利益？
- [ ] 是否包含开场钩子、卖点证明、适合人群和行动引导？
- [ ] 是否能被销售/客服复用为讲解话术？

### B. 平台适配
- [ ] 是否符合{platform}的内容节奏：{playbook['rhythm']}
- [ ] 前 3 秒是否能让用户理解“为什么要继续看”？
- [ ] 字幕是否足够简洁，单屏不堆砌过多信息？
- [ ] CTA 是否清晰，且与{content_goal}一致？

### C. 合规与可信度
- [ ] 是否避开禁忌点：{forbidden_claims}
- [ ] 是否避免绝对化用语，如“最、第一、100%、永久、根治”？
- [ ] 效果表达是否有场景限定和条件说明？
- [ ] 是否避免无法证明的竞品贬低或虚假对比？
""".strip()

    faq_items = [
        ("这款产品最适合谁？", f"更适合{target_user}，尤其是主要用于{use_case}、并且关注“{first_point}”的人群。"),
        ("它和普通同类产品的差异是什么？", f"建议从使用场景和实际体验解释：它的重点不是单一参数，而是围绕{', '.join(selling_points[:3])}形成完整购买理由。"),
        ("价格为什么在这个区间？", f"{price_range}对应的是目标用户对品质、体验、服务或场景适配的综合预期，销售时应结合具体卖点解释价值。"),
        ("使用时有什么需要注意？", f"需要明确告知边界：{forbidden_claims}。避免让用户产生超出产品能力的预期。"),
        ("买回去不适合怎么办？", "建议客服结合平台售后规则回答，并先通过使用场景、需求强度和购买顾虑判断是否适合。"),
        ("内容里最该强调哪一点？", f"优先强调“{first_point}”，因为它最容易和用户的真实场景建立连接。"),
    ]
    modules[MODULE_TITLES[8]] = """
| 问题 | 建议回答 |
| --- | --- |
%s
""".strip() % "\n".join([f"| {q} | {a} |" for q, a in faq_items])

    modules[MODULE_TITLES[9]] = f"""
1. **沉淀为单品内容模板：** 本次输出可作为{category}类目的标准工作流，后续只需替换商品资料即可快速生成新方案。  
2. **拆分给不同团队使用：** 运营使用卖点拆解和选题方案，内容团队使用脚本和 Prompt，销售团队使用 FAQ 和转化话术。  
3. **建立平台版本库：** 针对{platform}保留当前版本，同时可扩展为小红书笔记版、直播讲解版、详情页版和客服话术版。  
4. **加入数据反馈闭环：** 发布后记录播放完成率、点击率、咨询率、转化率，把高表现话术回填到模板中。  
5. **未来接入大模型 API：** 当前项目已经预留 API 模式，可在侧边栏配置模型、Base URL 和 API Key，让模型生成更灵活的业务交付文档。
""".strip()

    return modules
