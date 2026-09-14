import json
import os
from http.server import BaseHTTPRequestHandler

# ============================================================================
# 候选人资料片段（按主题拆分，检索时只取相关片段，避免每次发送完整简历）
# ============================================================================

CANDIDATE_FRAGMENTS = {
    "basic_info": """基本信息：
- 姓名：张文远
- 年龄：26 岁
- 前端开发经验：5 年
- 求职方向：前端开发工程师，专注企业级应用开发
- 期望城市：沈阳
- 学历：东北农业大学大专，计算机科学与技术专业，2020-2022 年""",

    "core_skills": """核心技术栈：
- 框架：Vue 2 / Vue 3、Vue Router、Vuex / Pinia、Axios
- UI 库：若依、Element UI / Element Plus、ECharts
- 技术领域：企业级后台系统、组件封装、工程化、多端 H5 开发
- 权限体系：RBAC（菜单、按钮、部门、数据范围）
- 测试：Cypress E2E 自动化测试
- 业务能力：复杂表单、业务流程、状态管理""",

    "work_history": """工作经历：

【东软云科技（沈阳）| 前端开发工程师 | 2024.04 - 至今】
- 负责宝马 BMW 内部核心业务系统前端开发和维护
- 参与并推进 Cypress 自动化测试体系建设
- 开发自动化脚本和 Jira 工单助手工具
- 参与企业级工程化、组件和业务能力建设

【上海思芮信息科技 | 前端开发工程师 | 2022.02 - 2024.04】
- 负责宝马 BMW 内部核心业务系统前端开发
- 参与工程化、组件封装和质量建设
- 与产品、后端团队协作完成复杂业务功能
- 2024 年 4 月转正加入东软云科技

【哈尔滨上承科技开发有限公司 | 前端开发工程师 | 2021.03 - 2022.01】
- 负责联通行政办公平台前端开发
- 涉及 PC、H5、APP 内嵌等多端场景
- 参与多端兼容和数据同步处理
- 后期担任前端小组长并参与北京联通总部交付""",

    "project_web_analyzer": """Web Analyzer（宝马 BBA | 300+ 站点监控平台）项目：
- 针对 300+ 站点核心链路编写 Cypress E2E 自动化脚本
- 开发自动化工单填写工具，单次处理时间从约 2 分钟缩短至约 20 秒
- 相关技术资产被甲方采纳为标准工具并持续使用""",

    "project_sddc": """SDDC Automation（企业级私有云管理平台）项目：
- 参与前端从 0 到 1 的架构和工程化建设
- 参与和负责 RBAC 权限体系设计与落地，覆盖菜单、按钮、部门和数据范围
- 实现虚拟机全生命周期相关功能
- 参与远程控制台、运维监控、ECharts 可视化开发
- 沉淀公共组件和业务组件库""",

    "project_360pm": """360PM（碧桂园工程管理平台）项目：
- 工程文档中心、多级文件管理、大文件上传、在线预览功能
- 数据可视化首页开发""",

    "project_unicom": """联通行政办公平台项目：
- PC + H5 + APP 内嵌多端开发
- 多端数据同步和兼容处理
- 后期担任前端小组长，参与北京联通总部交付""",

    "ai_project": """AI 相关实践：
- 近期通过 vibecoding 独立实践 AI 应用开发
- 实际使用 Prompt 设计、对话上下文管理、LLM API 调用
- 使用大模型 API + Vercel Serverless 部署
- 没有实际使用 Tool Calling、LangGraph、向量数据库等复杂 Agent 技术""",

    "answer_rules": """回答规则和行为准则：

【回答长度】
- 默认回答 80～180 字，普通问题 2～4 句话
- 只有明确要求详细解释时才展开
- 第一轮回答简洁，追问后再深入

【项目问题回答结构】
- 项目是什么、我负责什么、1～2 个重点、结果

【技术问题回答策略】
- 优先结合真实项目回答，特别是 Vue、Cypress、工程化、RBAC
- 严格区分"做过"、"参与过"、"了解但没实践"
- 资料没有明确说明实现方式时，不要自行补充底层细节

【AI 项目相关】
- 只介绍实际实现的内容，不虚构高级 Agent 能力

【语气和表达】
- 像真实的 5 年前端工程师，自然、自信、简洁
- 不使用"这个很简单""我只是学习""经验不足"等自我弱化表达
- 对不会或未实践的技术，直接说明目前没有实际实践
- 不要创造新的数字、效率指标或项目成果
- 不要把团队成果全部说成个人独立完成"""
}

# 各片段对应的检索关键词（命中越多，相关度越高）
FRAGMENT_KEYWORDS = {
    "basic_info": ["姓名", "年龄", "多大", "几岁", "学历", "学校", "毕业", "专业",
                   "哪里", "城市", "沈阳", "求职", "期望薪资", "籍贯", "介绍自己",
                   "自我介绍", "基本情况", "几年经验"],
    "core_skills": ["技术栈", "技能", "会什么", "擅长", "vue", "react", "js", "javascript",
                    "typescript", "ts", "element", "echarts", "axios", "pinia", "vuex",
                    "组件", "工程化", "h5", "前端", "状态管理", "ui"],
    "work_history": ["工作经历", "工作", "公司", "任职", "跳槽", "离职", "东软", "思芮",
                     "上承", "在职", "为什么换", "职业", "经历", "简历", "几年",
                     "负责什么", "做过多久", "履历"],
    # 带 "|" 前缀的是通用词，权重减半，避免"项目"这类词让所有项目片段并列
    "project_web_analyzer": ["cypress", "自动化测试", "e2e", "站点", "web analyzer",
                             "工单", "jira", "自动化脚本", "宝马", "bmw", "bba",
                             "|项目", "|测试"],
    "project_sddc": ["sddc", "私有云", "rbac", "菜单", "数据范围", "虚拟化",
                     "从0到1", "组件库", "权限体系", "|权限", "|架构",
                     "|项目", "|宝马", "|bmw"],
    "project_360pm": ["360pm", "碧桂园", "文件管理", "上传", "预览", "大文件",
                      "工程管理", "文档中心", "|项目"],
    "project_unicom": ["联通", "行政办公", "小组长", "app内嵌", "多端", "数据同步",
                       "北京联通", "移动端", "|项目"],
    "ai_project": ["ai", "人工智能", "大模型", "llm", "prompt", "agent", "智能体",
                   "rag", "langchain", "langgraph", "向量", "vibecoding", "gpt",
                   "对话", "vibe", "自己做的"],
    "answer_rules": [],
}

# 无论问什么都必须携带的片段（行为准则）
ALWAYS_INCLUDE = ("answer_rules",)


def _retrieve_context(query: str, max_fragments: int = 3) -> str:
    """根据问题检索最相关的资料片段（本地关键词匹配，无网络开销）"""
    q = query.lower()
    # 问的是 AI 方向时，压制其它项目片段的通用词权重，
    # 否则"讲讲你做的 AI 项目"会把四个业务项目一起带出来
    ai_focused = any(kw in q for kw in ("ai", "大模型", "llm", "智能体", "prompt", "agent"))
    scored = []

    for name, keywords in FRAGMENT_KEYWORDS.items():
        if not keywords:
            continue
        specific = 0.0   # 特征词命中（如 cypress、联通）
        generic = 0.0    # 通用词命中（如 项目）
        for kw in keywords:
            if kw.startswith("|"):
                if kw[1:] in q:
                    generic += 1.0
            elif kw in q:
                specific += 1.0
        if ai_focused and name.startswith("project_"):
            generic *= 0.2
        if specific or generic:
            # 特征词优先：让"做过哪些项目"能带出全部项目片段，
            # 而"cypress 怎么用的"只带出最相关的那个
            scored.append((specific * 10 + generic, name))

    # 分数降序，同分按名称稳定排序
    scored.sort(key=lambda x: (-x[0], x[1]))
    selected = list(ALWAYS_INCLUDE) + [name for _, name in scored[:max_fragments]]

    # 去重并保持顺序
    seen = set()
    ordered = [n for n in selected if not (n in seen or seen.add(n))]

    parts = []
    for name in ordered:
        parts.append(f"【{name}】\n{CANDIDATE_FRAGMENTS[name]}")

    # 一个关键词都没命中时，兜底给基本信息和技能
    if not scored:
        parts.insert(0, f"【basic_info】\n{CANDIDATE_FRAGMENTS['basic_info']}")
        parts.insert(1, f"【core_skills】\n{CANDIDATE_FRAGMENTS['core_skills']}")

    return "\n\n".join(parts)


def _build_system_prompt(query: str, top_k: int = 3) -> str:
    """构建 system prompt：精简的角色设定 + 检索到的相关资料"""
    context = _retrieve_context(query, top_k)
    return (
        "你是张文远的 AI 面试代理，请以张文远本人身份，自然、专业、真实地回答面试官问题。\n\n"
        "【最重要的规则】\n"
        "下面参考信息是唯一的事实来源。你只能使用其中明确写到的内容。\n"
        "- 不要补充参考信息里没有的实现细节、技术方案、组件名、API 名、数据流或架构设计。\n"
        "- 参考信息只说“参与/负责了某模块”时，就只讲这一层，不要展开内部是怎么实现的。\n"
        "- 参考信息里没提到的技术，直接说没有相关经验，不要推测或编造。\n"
        "- 不要新增数字、指标、项目成果或时间。\n"
        "- 团队成果不要说成个人独立完成。\n"
        "- 宁可回答得简短一些，也不要为了显得充实而补充细节。\n\n"
        f"=== 参考信息 ===\n{context}\n=== 参考信息结束 ==="
    )


class handler(BaseHTTPRequestHandler):
    """Vercel Python Serverless Function"""

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        # 健康检查：确认函数存活
        self._send_json({"status": "ok", "message": "AI Agent 后端运行中，请用 POST 调用"})

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0) or 0)
            raw = self.rfile.read(length) if length else b"{}"
            body = json.loads(raw.decode("utf-8"))
            messages = body.get("messages", [])

            # 只保留最近 6 条，防止超长
            messages = messages[-6:]

            if not messages or not messages[-1].get("content"):
                return self._send_json({"response": "你好！我是张文远的 AI 代理，有什么想问的？"})

            # 用最后一条用户消息做检索，拼接相关资料作为 system prompt
            llm_messages = [{"role": "system", "content": _build_system_prompt(messages[-1]["content"])}]
            for m in messages:
                role = m.get("role", "user")
                if role in ("user", "assistant"):
                    llm_messages.append({"role": role, "content": m.get("content", "")})

            # 调用 DeepSeek 官方接口（OpenAI 兼容）
            from openai import OpenAI
            client = OpenAI(
                api_key=os.getenv("DEEPSEEK_API_KEY", ""),
                base_url="https://api.deepseek.com",
            )

            response = client.chat.completions.create(
                model="deepseek-flash",
                messages=llm_messages,
                temperature=0.5,
                max_tokens=350,
            )

            result = response.choices[0].message.content
            self._send_json({"response": result})

        except Exception as e:
            self._send_json({"response": f"抱歉，出错了：{str(e)}"}, status=500)
