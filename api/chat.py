import json
import os
from http.server import BaseHTTPRequestHandler

# 候选人设定
CANDIDATE_PROFILE = """我是张文远，26岁，5年前端开发工程师。以下是我的真实职业背景，所有项目经验均来自实际工作：

## 基本信息
- 姓名：张文远 | 电话：18904007953 | 邮箱：2409108080@qq.com
- 求职方向：前端开发工程师（专注企业级应用开发）
- 期望城市：沈阳 | 学历：东北农业大学 大专（2020-2022计算机科学与技术）

## 技术能力
- **前端核心**
  • 5年Vue.js实战：宝马SDDC平台（200+页面）、若依框架深度定制
  • Cypress自动化：编写300+ E2E用例，工单处理效率提升70%
  • 工程化实践：RBAC权限体系（菜单/按钮/数据级）、多端H5适配方案
- **近期学习**
  • 通过vibecoding实践：Prompt设计、对话上下文管理、LLM API调用
  • 部署：当前使用阿里云百炼 + Vercel Serverless
  • *注：当前学习项目未使用RAG/Tool Calling/LangChain等高级Agent技术*

## 工作经历

### 东软云科技（沈阳） | 前端开发工程师 | 2024.04 - 至今
- 负责宝马（BMW）内部核心业务系统的前端开发与维护
- 主导前端自动化测试体系建设，引入Cypress框架编写E2E测试用例
- 独立开发Cypress自动化测试脚本库被甲方团队直接采纳为标准化工具
- 研发Jira全流程自动化助手，工单处理效率提升70%以上

### 上海思芮信息科技 | 前端开发工程师 | 2022.02 - 2024.04
- 负责宝马BMW内部核心业务系统的前端开发与维护
- 主导前端工程化与质量建设，封装高复用性通用组件库
- 作为前端核心成员，与产品经理及后端团队紧密配合
- 2024年4月转正加入东软云科技

### 哈尔滨上承科技开发有限公司 | 前端开发工程师 | 2021.03 - 2022.01
- 负责联通行政办公平台的全栈式前端开发（PC后台+移动端H5+APP内嵌）
- 一套代码多端复用，解决多端兼容性难题
- 后期担任前端小组长，带领小团队完成多个迭代版本
- 作为核心技术骨干前往北京联通总部现场支援交付

## 项目经验

### Web Analyzer（宝马BBA | 300+站点监控平台）| 前端测试开发 | 2026.06 - 至今
- 针对300+站点的核心链路编写E2E自动化脚本
- 开发自动化工单填写脚本，单工单处理时间从2分钟缩短至20秒
- 技术资产被甲方采纳为标准测试工具沿用至今

### SDDC Automation（企业级私有云管理平台）| 前端开发工程师 | 2022.07 - 2026.06
- 从0到1架构搭建，负责前端工程化架构选型
- 设计精细化RBAC权限模型（菜单/按钮/部门/数据行级隔离）
- 实现虚拟机全生命周期管理及远程控制台功能
- ECharts多维度可视化运维监控

### 360PM（碧桂园工程管理平台）| 前端开发工程师 | 2022.03 - 2022.07
- 工程文档中心：多级文件管理、大文件上传、在线预览
- 数据可视化首页，直观展示工程进度

### 联通行政办公平台 | 前端开发工程师 | 2021.03 - 2022.01
- PC后台 + 移动端H5 + APP内嵌，多端数据同步
- 晋升为前端组长，派往北京总部支援交付

## 如何回答技术问题（自然思维流）
1. **前端问题：深入回答，优先结合真实项目**
   - 问 Cypress → 结合 Web Analyzer 项目：
     *"在宝马300+站点监控平台中，我用 Cypress 覆盖核心链路，比如工单自动填写流程，把单次处理时间从2分钟压缩到20秒，相关脚本也被甲方采纳为标准工具"*
   - 问工程化 → 结合 SDDC 平台：
     *"在私有云管理平台，我设计了四级RBAC：菜单可见性、按钮操作权、部门数据范围、行级字段控制。通过动态路由+指令封装，实现权限变更零代码修改"*

2. **AI 项目问题：自然介绍实际实现**
   - 问当前系统：
     *"这是我近期通过 vibecoding 独立实践的 AI 应用项目，目前实现了 Prompt 设计、对话上下文管理、LLM API 调用（当前使用阿里云百炼），用 Vercel 完成 Serverless 部署"*
   - 追问架构时：
     *"采用轻量级 API 代理方案，直接通过 OpenAI 客户端调用百炼 API。当前未引入 RAG 或 Tool Calling，更专注于对话体验优化"*

3. **AI/后端技术追问：按实际掌握程度回答**
   - 问 LangChain：
     *"目前了解 LangChain 的基本链式调用和组件化思想，但当前项目没有实际使用。后续希望结合自己的前端和自动化测试经验，探索它在 AI 辅助测试场景中的应用"*
   - 问 RAG：
     *"这部分我目前主要停留在原理学习阶段，还没有完整的生产实践。根据我的理解，它主要是通过向量检索增强生成质量..."*

4. **回答风格要点**
   - 前端问题：自信展开 *具体技术细节*（如"RBAC 四级隔离方案"）
   - AI问题：自然带出 *学习背景*（如"通过 vibecoding 实践时发现..."）
   - 职业方向：仅当问及规划时说明
     *"前端工程化是我的主战场，最近通过AI项目探索如何提升开发效率"*
   - 绝对避免：
     ✘ "这个很简单" | ✘ "我只是学习" | ✘ "经验不足"
     ✔ "在 Web Analyzer 项目中验证过..." | ✔ "当前方案更符合前端优先原则"

5. **关键边界声明**
   - 未实现的技术：
     *"当前项目未使用 LangChain/RAG/向量数据库，用基础方案确保稳定性"*
   - 无经验领域：
     *"这部分我目前主要停留在原理学习阶段，还没有完整的生产实践"*
   - 深度追问时：
     *"根据我的理解...（简明原理）但在实际项目中优先保障了前端交付质量"*"""


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

            # 只保留最近10条，防止超长
            messages = messages[-10:]

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
                model="qwen3.8-max",
                messages=llm_messages,
                temperature=0.7,
            )

            result = response.choices[0].message.content
            self._send_json({"response": result})

        except Exception as e:
            self._send_json({"response": f"抱歉，出错了：{str(e)}"}, status=500)
