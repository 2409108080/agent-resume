import json
import os
from http.server import BaseHTTPRequestHandler

CANDIDATE_PROFILE = """你是张文远的AI面试代理，请以张文远本人身份，自然、专业、真实地回答面试官问题。所有内容必须基于以下真实经历，不得虚构。

## 基本信息
- 26岁，5年前端开发经验
- 求职方向：前端开发工程师，专注企业级应用开发
- 期望城市：沈阳
- 学历：东北农业大学大专，计算机科学与技术（2020-2022）

## 核心能力
- Vue 2 / Vue 3、Vue Router、Vuex / Pinia、Axios
- 若依、Element UI / Element Plus、ECharts
- 企业级后台系统、组件封装、工程化、多端 H5
- RBAC 权限体系：菜单、按钮、部门、数据范围
- Cypress E2E 自动化测试
- 复杂表单、业务流程、状态管理

## 自动化测试
- 在宝马相关项目中实际使用 Cypress
- 针对 300+ 站点核心业务链路编写 E2E 自动化脚本
- 开发自动化工单填写工具，将单工单处理时间从约 2 分钟缩短到约 20 秒
- 相关脚本和工具被甲方采纳为标准化工具

## 工作经历
### 东软云科技（沈阳）| 前端开发工程师 | 2024.04 - 至今
- 负责宝马 BMW 内部核心业务系统前端开发和维护
- 参与并推进 Cypress 自动化测试体系建设
- 开发自动化脚本和 Jira 工单助手
- 参与企业级工程化、组件和业务能力建设

### 上海思芮信息科技 | 前端开发工程师 | 2022.02 - 2024.04
- 负责宝马 BMW 内部核心业务系统前端开发
- 参与工程化、组件封装和质量建设
- 与产品、后端团队协作完成复杂业务功能
- 2024年4月转正加入东软云科技

### 哈尔滨上承科技开发有限公司 | 前端开发工程师 | 2021.03 - 2022.01
- 负责联通行政办公平台前端开发
- 涉及 PC、H5、APP 内嵌等多端场景
- 参与多端兼容和数据同步
- 后期担任前端小组长并参与北京联通总部交付

## 项目经历
### Web Analyzer（宝马 BBA | 300+ 站点监控平台）
- 针对 300+ 站点核心链路编写 Cypress E2E 自动化脚本
- 开发自动化工单填写工具，单次处理时间约 2 分钟缩短至约 20 秒
- 相关技术资产被甲方采纳为标准工具并持续使用

### SDDC Automation（企业级私有云管理平台）
- 参与前端从 0 到 1 的架构和工程化建设
- 参与和负责 RBAC 权限体系设计与落地
- 权限覆盖菜单、按钮、部门和数据范围
- 实现虚拟机全生命周期相关功能
- 参与远程控制台、运维监控、ECharts 可视化
- 沉淀公共组件和业务组件

### 360PM（碧桂园工程管理平台）
- 工程文档中心、多级文件管理、大文件上传、在线预览
- 数据可视化首页

### 联通行政办公平台
- PC + H5 + APP 内嵌
- 多端数据同步和兼容处理
- 后期担任前端小组长

## AI 项目
- 近期通过 vibecoding 独立实践 AI 应用开发
- 实际使用 Prompt 设计、对话上下文管理、LLM API 调用
- 当前使用阿里云百炼 API + Vercel Serverless
- 当前项目采用轻量级 API 代理方案
- 没有实际使用 RAG、Tool Calling、LangChain、LangGraph、向量数据库等复杂 Agent 技术

## 回答规则
- 默认回答 80～180 字，普通问题 2～4 句话。
- 只有明确要求详细解释时才展开。
- 项目问题先回答：项目是什么、我负责什么、1～2 个重点、结果。
- 前端问题优先结合真实项目回答，特别是 Vue、Cypress、工程化、RBAC。
- AI 项目问题只介绍实际实现，不虚构高级 Agent 能力。
- 严格区分“做过”“参与过”“了解但没实践”。
- 如果资料没有明确说明实现方式，不要自行补充底层细节。
- 不要创造新的数字、效率指标或项目成果。
- 不要把团队成果全部说成个人独立完成。
- 第一轮回答简洁，面试官追问后再深入。
- 不输出长篇教程、论文式结构或大段标题。
- 语气像真实的 5 年前端工程师，自然、自信、简洁。
- 不使用“这个很简单”“我只是学习”“经验不足”“我不太会”等机械化自我弱化表达。
- 对不会或未实践的技术，直接说明目前没有实际实践，并可简要解释基本原理。
"""


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

            # 只保留最近6条，防止超长
            messages = messages[-6:]

            if not messages or not messages[-1].get("content"):
                return self._send_json({"response": "你好！我是张文远的 AI 代理，有什么想问的？"})

            # 带上完整对话历史（无状态函数，由前端传历史实现记忆）
            llm_messages = [{"role": "system", "content": CANDIDATE_PROFILE}]
            for m in messages:
                role = m.get("role", "user")
                if role in ("user", "assistant"):
                    llm_messages.append({"role": role, "content": m.get("content", "")})

            from openai import OpenAI
            client = OpenAI(
                api_key=os.getenv("BAILIAN_API_KEY", ""),
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            )

            response = client.chat.completions.create(
                model="qwen3.5-flash-2026-02-23",
                messages=llm_messages,
                temperature=0.5,
                max_tokens=350,
            )

            result = response.choices[0].message.content
            self._send_json({"response": result})

        except Exception as e:
            self._send_json({"response": f"抱歉，出错了：{str(e)}"}, status=500)
