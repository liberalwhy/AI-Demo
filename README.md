# ecom-content-agent

一个可本地运行、也可以接入大模型 API 的 **电商内容工作流 Agent Demo**，适合放入求职作品集，展示你如何把电商内容生产流程拆解为结构化、可复用、可交付的 AI 工作流。

> 重要说明：这个项目不是单纯生成文案，而是把电商内容生产流程拆解成可复用、可培训、可交付的 AI 工作流 Demo。

## 项目定位

`ecom-content-agent` 面向电商运营、内容团队、销售团队。用户输入商品资料后，系统会自动生成一份偏真实业务交付格式的内容工作流文档，包括：

1. 商品信息摘要
2. 核心卖点拆解
3. 用户痛点与内容切入角度
4. 3 套短视频内容方案
5. 1 条完整短视频脚本
6. AI 画面/视频 Prompt
7. 生产 SOP
8. 质检清单
9. 销售/客户 FAQ
10. 可复用建议

## 当前版本新增能力

这个版本支持两种生成引擎：

### 1. 本地模板模式

- 不需要 API Key
- 不需要联网
- 适合基础演示、面试讲解、GitHub 展示
- 内容由规则 + 模板生成，稳定但创意有限

### 2. 大模型 API 模式

- 支持 OpenAI-compatible Chat Completions 接口
- 可接 OpenAI、DeepSeek、Kimi / Moonshot 等兼容服务
- 可在页面侧边栏填写 API Key、Base URL、模型名称
- API 失败时可以自动切回本地模板模式
- 脚本、选题、FAQ 和 Prompt 质量会明显优于纯模板模式

## Demo 价值

这个 Demo 重点展示的不是“会写几句广告文案”，而是：

- 如何把商品信息转化成业务团队能用的内容资产
- 如何把卖点、痛点、脚本、Prompt、SOP、质检和 FAQ 串成完整流程
- 如何让 AI 输出更接近真实工作交付，而不是普通聊天回答
- 如何为运营、内容、销售团队提供统一的内容生产框架
- 如何设计一个可扩展的 Agent 型 SaaS 工具原型
- 如何从本地规则版本平滑升级到真实大模型 API 版本

适合在面试或作品集中说明：你理解业务流程、内容生产链路、AI 工具产品化和交付标准。

## 技术栈

- Python
- Streamlit
- OpenAI Python SDK
- 本地规则引擎 + OpenAI-compatible LLM API

## 项目结构

```text
ecom-content-agent/
├── app.py                         # Streamlit 主应用
├── models.py                      # 数据结构和输出模块定义
├── local_generator.py             # 本地规则 + 模板生成器
├── llm_client.py                  # 大模型 API 调用封装
├── prompt_templates.py            # 大模型提示词模板
├── requirements.txt               # Python 依赖
├── README.md                      # 项目说明
├── sample_input.md                # 示例输入
├── .env.example                   # 本地环境变量示例
├── .gitignore                     # Git 忽略配置
└── .streamlit/
    └── secrets.toml.example       # Streamlit Secrets 示例
```

## 本地运行方式

### 1. 进入项目目录

Windows 示例：

```bash
cd /d C:\Users\86159\anaconda3\envs\pytorch\codes\ecom-content-agent
```

普通路径示例：

```bash
cd ecom-content-agent
```

### 2. 安装依赖

如果你的电脑可以直接使用 pip：

```bash
pip install -r requirements.txt
```

如果你之前遇到过 `'pip' 不是内部或外部命令`，请用：

```bash
python -m pip install -r requirements.txt
```

如果你使用 Anaconda 环境：

```bash
conda activate pytorch
python -m pip install -r requirements.txt
```

### 3. 启动 Streamlit

```bash
python -m streamlit run app.py
```

浏览器打开：

```text
http://localhost:8501
```

## 如何使用本地模板模式

1. 启动项目
2. 侧边栏选择：`本地模板模式`
3. 填写商品资料
4. 点击 `生成内容工作流文档`
5. 查看输出结果或下载 Markdown 文档

本地模板模式不调用任何外部 API，适合确认项目是否正常运行。

## 如何接入大模型 API

启动页面后，在左侧侧边栏选择：

```text
大模型 API 模式
```

然后填写：

```text
API Key
Base URL
模型名称
temperature
最大输出 tokens
```

### OpenAI 示例

```text
Base URL: https://api.openai.com/v1
Model: 按你的账号可用模型填写，例如 gpt-4o-mini
```

### DeepSeek 示例

```text
Base URL: https://api.deepseek.com
Model: deepseek-chat
```

### Kimi / Moonshot 示例

```text
Base URL: https://api.moonshot.cn/v1
Model: moonshot-v1-8k
```

不同服务商的 Base URL 和模型名称可能会更新，请以对应服务商后台文档为准。

## 通过环境变量配置 API

你也可以不在页面里手动输入，而是通过环境变量配置。

### Windows CMD

```bash
set LLM_API_KEY=你的APIKey
set LLM_BASE_URL=https://api.openai.com/v1
set LLM_MODEL=gpt-4o-mini
python -m streamlit run app.py
```

### Windows PowerShell

```powershell
$env:LLM_API_KEY="你的APIKey"
$env:LLM_BASE_URL="https://api.openai.com/v1"
$env:LLM_MODEL="gpt-4o-mini"
python -m streamlit run app.py
```

### macOS / Linux

```bash
export LLM_API_KEY="你的APIKey"
export LLM_BASE_URL="https://api.openai.com/v1"
export LLM_MODEL="gpt-4o-mini"
python -m streamlit run app.py
```

## 部署到 Streamlit Cloud 时如何配置 API Key

如果你把项目放到 GitHub 并部署到 Streamlit Community Cloud：

1. 不要把真实 API Key 写进代码
2. 不要提交 `.streamlit/secrets.toml`
3. 在 Streamlit Cloud 后台找到你的 App
4. 进入 `Settings` / `Secrets`
5. 添加：

```toml
LLM_API_KEY = "你的APIKey"
LLM_BASE_URL = "https://api.openai.com/v1"
LLM_MODEL = "gpt-4o-mini"
```

项目里的 `.streamlit/secrets.toml.example` 只是示例文件，可以提交到 GitHub；真正的 `secrets.toml` 不要提交。

## 输入字段

页面包含以下商品资料字段：

- 商品名称
- 商品品类
- 核心卖点
- 目标用户
- 售卖平台
- 内容目标
- 价格区间
- 使用场景
- 禁忌/不能夸大的点
- 参考风格

## 输出特点

生成结果会尽量以真实业务交付文档的形式呈现，而不是聊天式回答。输出内容强调：

- 表格化卖点拆解
- 痛点和内容切入角度
- 短视频方案和脚本分镜
- 可直接给 AI 绘图/视频工具使用的 Prompt
- 团队协作 SOP
- 发布前质检清单
- 销售和客服可复用 FAQ
- 后续内容资产复用建议

## 核心代码说明

### `app.py`

负责 Streamlit 页面、表单、侧边栏 API 配置、结果展示和 Markdown 下载。

### `local_generator.py`

负责本地规则 + 模板生成。没有 API Key 时也可以正常运行。

### `llm_client.py`

负责调用 OpenAI-compatible API：

```python
response = client.chat.completions.create(
    model=config.model,
    messages=messages,
    temperature=config.temperature,
    max_tokens=config.max_tokens,
)
```

### `prompt_templates.py`

负责构造系统提示词和用户提示词，要求模型返回固定 10 个模块的 JSON。

## 后续可扩展方向

1. **接入真实 OpenAI Responses API**  
   当前为了兼容多个服务商，使用 Chat Completions 风格。后续如果只接 OpenAI，可以升级为 Responses API。

2. **JSON Schema / Pydantic 校验**  
   对模型输出做更严格的字段校验，避免格式错误。

3. **行业知识库 / RAG**  
   接入品牌手册、历史爆款脚本、用户评价、竞品资料，让生成结果更贴近品牌和行业。

4. **平台模板库**  
   针对抖音、小红书、淘宝、天猫、京东、亚马逊等平台建立差异化内容模板。

5. **内容合规检查**  
   增加敏感词、绝对化用语、医疗功效、虚假承诺、平台规则等检查模块。

6. **导出多格式文档**  
   支持导出 Markdown、PDF、Word、PPT 或飞书/Notion 文档。

7. **数据复盘闭环**  
   记录每条内容的播放率、点击率、咨询率、转化率，把高表现话术回填到模板。

8. **多角色协同**  
   将输出拆分给运营、编导、设计、拍摄、销售和客服使用，形成完整内容生产看板。

## 适合作品集展示的讲解角度

面试时可以这样介绍：

> 我做的不是一个简单的文案生成器，而是一个电商内容生产工作流 Agent Demo。它把商品资料输入后，自动拆解为运营能看懂的卖点、内容团队能执行的脚本和 Prompt、销售团队能复用的 FAQ，同时包含 SOP 和质检标准。这个结构既可以本地模板化运行，也可以切换到大模型 API 模式，后续还能接入品牌知识库和数据复盘系统，演进为真实的内容生产 SaaS 工具。

## 安全提醒

- 不要把真实 API Key 上传到 GitHub
- 不要把真实 API Key 写死在 `app.py`
- 本地测试可以在页面填写 API Key
- 部署线上建议使用 Streamlit Secrets 或环境变量

## License

MIT License
