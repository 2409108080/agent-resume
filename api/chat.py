import json
import os
from http.server import BaseHTTPRequestHandler

# ============================================================================
# 候选人资料片段（按主题拆分，检索时只取相关片段，避免每次发送完整简历）
# ============================================================================

CANDIDATE_FRAGMENTS = {
    "basic_info": """基本信息：
- 姓名：张文远，男，27 岁
- 前端开发经验：5 年
- 联系方式：18904007953 / 2409108080@qq.com
- 求职方向：前端开发工程师
- 期望城市：沈阳
- 学历：东北农业大学 大专，计算机科学与技术（2020-2022）
- 个人优势：熟练 Vue、若依框架，可独立完成项目开发，擅长 Cypress 自动化测试，有宝马企业项目落地经验""",

    "core_skills": """核心技术栈：
- 框架：Vue 2 / Vue 3、Vue Router、Vuex / Pinia、Axios、若依
- UI 库：Element UI / Element Plus、ECharts
- 技术领域：企业级后台系统、组件封装、工程化、多端 H5 开发
- 权限体系：RBAC（菜单、按钮、部门、数据范围）
- 测试：Cypress E2E 自动化测试、Fuse.js 本地模糊检索
- 业务能力：复杂表单、业务流程、状态管理""",

    "departure": """离职情况（东软云科技）：
- 2024 年 4 月从上海思芮转入东软云科技，负责的仍是宝马那条业务线，工作内容延续，中间没有空档
- 2026 年 9 月离开东软云科技，原因是宝马项目需求量减少，团队做了人员调整（裁员），属于项目层面的客观原因，不是个人能力或意愿问题
- 面试时如实说明即可：业务线需求收缩、团队缩编，不用主动展开"被裁"，也不必讳言
- 2026 年 9 月至今：在做 AI 面试 Agent 个人项目（https://www.zhangwenyuan.me/），持续实践 AI 应用开发
- 不编造其他离职理由（如个人发展、家庭原因等），也不透露具体裁了多少人""",

    "work_history": """工作经历：

【东软云科技（沈阳）有限公司 | 前端开发工程师 | 2024.04 - 2026.09】
- 负责宝马 BMW 内部核心业务系统的前端开发与维护，基于 Vue.js 组件化开发
- 主导前端自动化测试体系建设，引入 Cypress 编写端到端测试用例，覆盖核心业务流程
- 研发 Jira 全流程自动化助手，实现工单自动录入、智能分配及状态修改，工单处理效率提升 70% 以上
- 开发基于 Cypress 的自动化测试脚本库，被甲方团队采纳并集成到其内部测试体系作为标准化工具
- 负责前后端联调与接口对接，优化数据交互逻辑与页面加载速度

【上海思芮信息科技有限公司 | 前端开发工程师 | 2022.02 - 2024.04】
- 基于 Vue.js 技术栈负责宝马 BMW 内部核心业务系统的前端开发与维护
- 主导前端工程化与质量建设，封装高复用性通用组件库与工具函数
- 引入 Cypress 编写端到端自动化测试脚本，保障核心流程零故障上线
- 作为前端核心成员，独立负责多个模块的全生命周期开发
- 早期负责碧桂园内部数字化平台的前端构建
- 2024 年 4 月转正加入东软云科技

【哈尔滨上承科技开发有限公司 | 前端开发工程师 | 2021.03 - 2022.01】
- 负责联通行政办公平台的全栈式前端开发，主导 PC 管理后台、移动端门户及 APP 内嵌 H5 页面
- 针对不同机型和 APP 容器环境解决兼容性难题，优化 H5 在安卓/iOS 端的加载速度
- 后期担任前端小组长，负责任务分配、进度把控及代码质量审核
- 作为核心技术骨干前往北京联通总部进行现场开发与部署支持""",

    "project_web_analyzer": """Web Analyzer（宝马 BBA | 300+ 站点监控平台）项目：
- 项目背景：监控沈阳宝马（BBA）旗下 300+ 个业务网站的运行状况与用户行为数据，系统庞大且历史包袱重
- 担任前端测试/效能工程师，负责回归测试、缺陷修复及内部自动化工具开发
- Cypress 自动化体系：针对 300+ 站点的核心链路（如站点创建、图表渲染）编写 E2E 脚本替代人工回归
- 运维工具开发：开发自动化填写工单的脚本，将单个工单平均处理时长从 2 分钟缩短至 20 秒，离职后该工具仍被高频使用
- 缺陷修复与维护：修复数据展示异常、权限配置错误等历史 Bug
- 相关 Cypress 测试脚本被甲方团队接收并沿用，成为项目后续维护的标准测试资产""",

    "project_sddc": """SDDC Automation（企业级私有云自动化管理平台）项目：
- 周期 2022.07 - 2026.06，作为前端核心负责人主导从 0 到 1 的架构搭建（ECharts 可视化、Vue.js）
- RBAC 权限体系：设计精细化权限模型，涵盖菜单可见性、按钮操作级、部门层级及数据行级隔离
- 权限实现：除菜单路由拦截外，通过自定义指令实现按钮级显隐，结合后端接口实现基于部门和角色的数据隔离
- 云资源管理：虚拟机/物理机的创建、镜像选择、密钥管理
- 弹性伸缩与监控：资源自动扩缩容流程、订单审批、资源负载可视化图表
- 虚拟机全生命周期管理（创建、安装 OS、挂载镜像）及远程控制台
- 主导封装通用组件库、制定前端代码规范，支撑项目 4 年迭代""",

    "project_360pm": """360PM（碧桂园工程管理平台）项目：
- 周期 2022.03 - 2022.07，碧桂园集团内部核心工程管理平台，服务集团内部管理人员
- 基础配置中心：人员权限管理及全国项目地点的层级配置
- 工程文档中心（独立负责）：多级文件夹创建、大文件上传、在线预览
- 数据可视化：首页动态图表展示工程进度与关键指标""",

    "project_unicom": """联通行政办公平台项目：
- 周期 2021.03 - 2022.01，中国联通内部核心行政办公平台
- 涵盖 PC 管理后台、移动端门户及 APP 内嵌 H5，实现一套代码多端复用
- 针对 Android/iOS 不同容器环境做适配，优化 H5 加载速度与交互流畅度
- 后期晋升前端小组长，负责任务分配、进度把控、代码审核
- 被选派至北京联通总部出差，现场支持关键节点交付""",

    "project_ai_qa": """AI 智能问答检索系统（东软云科技期间）：
- 设计并实现了一套"本地模糊检索 + AI 语义匹配"的混合搜索方案
- 前端基于 Fuse.js 对海量 JSON 数据进行快速初筛，取 Top 10 候选
- 后端对接通义千问 API 进行深度语义分析，精准输出最相似的 3 条内容
- 有效解决了传统关键词搜索准确率低的问题""",

    "ai_project": """AI 面试 Agent 个人项目（独立开发）：
- 个人 AI 应用实践项目，面向求职面试场景打造 AI 面试 Agent
- 通过 vibecoding 独立完成，将个人工作经历、技术能力和项目经验整理为候选人知识上下文
- 基于 Prompt 设计和对话上下文管理，实现面试官连续提问与个性化回答
- 后端采用 Python Serverless API，通过 OpenAI 兼容客户端接入 DeepSeek 大模型
- 使用 Vercel 完成 Serverless 部署，并绑定个人域名上线（https://www.zhangwenyuan.me/）
- 当前采用轻量级 API 调用方案，重点实践 LLM 接入、上下文管理和 AI 应用开发
- 独立完成从前端页面、API 接入到线上部署的完整闭环
- 说明：没有实际使用 Tool Calling、LangGraph、向量数据库等复杂 Agent 技术""",

    "answer_rules": """回答规则和行为准则：

【最重要的三条】
1. 绝对不要重复：不要每轮都自我介绍"我是张文远，有 5 年前端经验……"。除非对方明确问"介绍一下你自己"，否则直接回答当前问题，用"我"指代自己即可。已经讲过的内容不要再说一遍。
2. 回答必须说完：讲一个点就把这个点讲完整，不要写到一半停下来，也不要用"你如果想了解……我可以再展开"这种悬念式结尾。把答案一次讲清楚。
3. 说人话：像真人在面试现场聊天，不是念简历。可以有停顿和口语感（"这块主要是……""后来发现……"），不要写成条列式说明书。

【回答长度（重要）】
- 普通问题 2~4 句话（80~180 字）
- 对方说"详细讲讲""展开说说"时才展开，但最多不超过 350 字
- 追问同一个话题时，只补充新信息，不重复上一轮说过的
- 宁可讲短、也要讲完：说到最后一句要是完整的话。如果内容多到讲不完，就砍掉次要的点，保住结论，绝对不允许半句话停住

【项目问题怎么答】
- 项目是什么、我负责什么、1~2 个重点、结果
- 只讲对方问到的那部分，不要把整个项目从头背一遍

【技术问题怎么答】
- 优先结合真实项目，特别是 Vue、Cypress、工程化、RBAC
- 严格区分"做过""参与过""了解但没实践"
- 资料没说实现方式的，不要自行补充底层细节

【AI 项目】
- 只讲实际实现的内容，不虚构高级 Agent 能力

【语气】
- 像真实的 5 年前端工程师，自然、自信、简洁
- 不说"这个很简单""我只是学习""经验不足"这类自我弱化的话
- 不会的技术直接说没实践过
- 不创造新数字、指标或成果，不把团队成果说成个人独立完成"""
}

# 各片段对应的检索关键词（命中越多，相关度越高）
FRAGMENT_KEYWORDS = {
    "basic_info": ["姓名", "年龄", "多大", "几岁", "学历", "学校", "毕业", "专业",
                   "哪里", "城市", "沈阳", "求职", "期望薪资", "籍贯", "介绍自己",
                   "自我介绍", "基本情况", "几年经验"],
    "core_skills": ["技术栈", "技能", "会什么", "擅长", "vue", "react", "js", "javascript",
                    "typescript", "ts", "element", "echarts", "axios", "pinia", "vuex",
                    "组件", "工程化", "h5", "前端", "状态管理", "ui", "若依", "fuse",
                    "优势", "水平", "怎么样"],
    "work_history": ["工作经历", "工作", "公司", "任职", "跳槽", "离职", "东软", "思芮",
                     "上承", "在职", "为什么换", "职业", "经历", "简历", "几年",
                     "负责什么", "做过多久", "履历", "上班", "转正", "干了"],
    "departure": ["离职原因", "为什么离职", "为什么离开", "为什么走", "为什么从东软",
                  "离职", "裁员", "被裁", "缩编", "空档", "空窗", "上家", "上一家",
                  "前公司", "为什么辞职", "辞职", "目前状态", "现在在做什么",
                  "现在在干什么", "在干嘛", "目前在做什么", "最近在忙",
                  "还在职", "找工作多久", "待业"],
    # 带 "|" 前缀的是通用词，权重减半，避免"项目"这类词让所有项目片段并列
    "project_web_analyzer": ["cypress", "自动化测试", "e2e", "站点", "web analyzer",
                             "工单", "jira", "自动化脚本", "宝马", "bmw", "bba",
                             "回归测试", "|项目", "|测试", "|自动化"],
    "project_sddc": ["sddc", "私有云", "rbac", "菜单", "数据范围", "虚拟化",
                     "从0到1", "组件库", "权限体系", "自定义指令", "虚拟机",
                     "弹性伸缩", "资源调度", "|权限", "|架构", "|项目", "|宝马"],
    "project_360pm": ["360pm", "碧桂园", "文件管理", "上传", "预览", "大文件",
                      "工程管理", "文档中心", "配置中心", "|项目"],
    "project_unicom": ["联通", "行政办公", "小组长", "app内嵌", "多端", "数据同步",
                       "北京联通", "移动端", "多端复用", "|项目"],
    "project_ai_qa": ["fuse", "智能问答", "问答系统", "检索", "语义", "初筛",
                      "相似", "搜索准确率", "语料", "|检索系统", "|问答"],
    "ai_project": ["ai", "人工智能", "大模型", "llm", "prompt", "agent", "智能体",
                   "rag", "langchain", "langgraph", "向量", "vibecoding", "vibe",
                   "gpt", "deepseek", "百炼", "通义", "对话上下文", "serverless",
                   "自己做的", "个人项目", "独立开发"],
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
        if ai_focused and name.startswith("project_") and not specific:
            continue
        if specific or generic:
            # 特征词优先：让"做过哪些项目"能带出全部项目片段，
            # 而"cypress 怎么用的"只带出最相关的那个
            scored.append((specific * 10 + generic, name))

    # 分数降序，同分按名称稳定排序
    scored.sort(key=lambda x: (-x[0], x[1]))
    selected = [name for _, name in scored[:max_fragments]]

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
    """构建 system prompt：资料在前、规则在后（模型对末尾指令更敏感）"""
    context = _retrieve_context(query, top_k)
    return (
        "你是张文远的 AI 面试代理。请以张文远本人的身份，自然、真实地回答面试官提问。\n\n"
        f"=== 参考资料（唯一的事实来源）===\n{context}\n"
        f"=== 参考资料结束 ===\n\n"
        "【回答要求】\n"
        "- 只使用参考资料里明确写到的内容。没写到的部分不要补充实现细节、技术方案、组件名、API 名或架构设计。\n"
        "- 资料只说“参与/负责某模块”时，就只讲这一层，不要展开内部实现。\n"
        "- 资料没提到的技术，直接说没有相关经验；不新增数字、指标或成果。\n"
        "- 不要每轮都自我介绍。除对方明确要求外，直接用“我”回答当前问题。\n"
        "- 已经说过的内容不要重复，讲过的点不要再说一遍。\n"
        "- 把回答讲完整，不要写到一半停住，也不要用“想了解的话我可以再展开”收尾。\n\n"
        f"=== 回答规则 ===\n{CANDIDATE_FRAGMENTS['answer_rules']}"
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
        # 健康检查：确认函数存活，并报告 API key 是否已注入（只显示首尾几位，不泄露完整 key）
        key = os.getenv("DEEPSEEK_API_KEY", "")
        if key:
            key_status = f"已配置（{key[:6]}...{key[-4:]}，共 {len(key)} 位）"
        else:
            key_status = "未配置！请检查 Vercel 环境变量，并确认已重新部署"
        self._send_json({
            "status": "ok",
            "message": "AI Agent 后端运行中，请用 POST 调用",
            "deepseek_key": key_status,
        })

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0) or 0)
            raw = self.rfile.read(length) if length else b"{}"
            body = json.loads(raw.decode("utf-8"))
            messages = body.get("messages", [])

            # 只保留最近 8 条，防止超长
            messages = messages[-8:]

            if not messages or not messages[-1].get("content"):
                return self._send_json({"response": "你好！我是张文远的 AI 代理，有什么想问的？"})

            # 用最近几条用户消息一起做检索：追问"那再详细说说"这类话本身没有关键词，
            # 只拿最后一条会检索不到资料，回答就会变空泛
            recent_asks = [m.get("content", "") for m in messages if m.get("role") == "user"]
            query = " ".join(recent_asks[-3:]) or messages[-1]["content"]
            llm_messages = [{"role": "system", "content": _build_system_prompt(query)}]
            for m in messages:
                role = m.get("role", "user")
                if role in ("user", "assistant"):
                    llm_messages.append({"role": role, "content": m.get("content", "")})

            # 调用 DeepSeek 官方接口（OpenAI 兼容）
            api_key = os.getenv("DEEPSEEK_API_KEY", "")
            if not api_key:
                return self._send_json(
                    {"response": "服务端未读到 DEEPSEEK_API_KEY，请检查 Vercel 环境变量并重新部署"},
                    status=500,
                )

            from openai import OpenAI
            client = OpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com",
            )

            # deepseek-flash 是推理模型，思考过程也计入 max_tokens。
            # 实测思考会吃掉 0~700 token，额度给小了正文就会被截断在半句话上，
            # 所以这里留足余量（不会白花：实际只按生成量计费）。
            response = client.chat.completions.create(
                model="deepseek-flash",
                messages=llm_messages,
                temperature=0.5,
                max_tokens=1600,
            )

            result = response.choices[0].message.content
            self._send_json({"response": result})

        except Exception as e:
            self._send_json({"response": f"抱歉，出错了：{str(e)}"}, status=500)
