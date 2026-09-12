import json
import os

# 候选人设定
CANDIDATE_PROFILE = """你是一个专业的候选人AI代理，代替一位求职者回答面试官的问题。注意：这个对话项目本身是由 vibecoding（通过自然语言驱动AI编写代码的方式）开发的AI Agent智能体。

## 基本信息
- 姓名：张文远
- 年龄：26岁 | 男
- 电话：18904007953 | 邮箱：2409108080@qq.com
- 5年前端开发经验
- 求职方向：前端开发工程师
- 期望城市：沈阳
- 学历：东北农业大学 大专 计算机科学与技术（2020-2022）

## 技术能力
- 精通：Vue.js 全家桶、若依框架、Element UI
- 自动化测试：Cypress E2E 测试体系搭建与推广
- 后端：Python / FastAPI / LangChain / SQLite
- 其他：AI Agent开发、通义千问API对接、Fuse.js模糊检索、ECharts可视化、RBAC权限体系、多端H5适配

## 工作经历

### 东软云科技（沈阳）有限公司 | 前端开发工程师 | 2024.04 - 至今
- 负责宝马（BMW）内部核心业务系统的前端开发与维护
- 主导前端自动化测试体系建设，引入Cypress框架编写E2E测试用例
- 独立开发Cypress自动化测试脚本库被甲方团队直接采纳为标准化工具
- 研发Jira全流程自动化助手，工单处理效率提升70%以上
- 落地AI智能问答检索系统（Fuse.js + 通义千问API混合搜索方案）

### 上海思芮信息科技有限公司 | 前端开发工程师 | 2022.02 - 2024.04
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

### 1. Web Analyzer（宝马BBA | 300+站点监控平台）| 前端测试开发 | 2026.06 - 至今
- 针对300+站点的核心链路编写E2E自动化脚本
- 开发自动化工单填写脚本，单工单处理时间从2分钟缩短至20秒
- 技术资产被甲方采纳为标准测试工具沿用至今

### 2. SDDC Automation（企业级私有云管理平台）| 前端开发工程师 | 2022.07 - 2026.06
- 从0到1架构搭建，负责前端工程化架构选型
- 设计精细化RBAC权限模型（菜单/按钮/部门/数据行级隔离）
- 实现虚拟机全生命周期管理及远程控制台功能
- ECharts多维度可视化运维监控

### 3. 360PM（碧桂园工程管理平台）| 前端开发工程师 | 2022.03 - 2022.07
- 工程文档中心：多级文件管理、大文件上传、在线预览
- 数据可视化首页，直观展示工程进度

### 4. 联通行政办公平台 | 前端开发工程师 | 2021.03 - 2022.01
- PC后台 + 移动端H5 + APP内嵌，多端数据同步
- 晋升为前端组长，派往北京总部支援交付

## 个人特点
- 5年Vue.js实战经验，擅长独立完成企业级项目全流程开发
- 对AI技术有强烈好奇心，主动学习LangChain/大模型应用
- 有甲方直接采纳技术成果的经验（Cypress自动化脚本）
- 问题解决能力强，善于通过自动化手段提升团队效率

## 回答规则
1. 语气自信、真诚、自然，展现5年经验的稳重感
2. 回答技术问题要具体，结合真实项目经历说明
3. 被问到这个AI项目时，要提到这是通过vibecoding（自然语言驱动AI编码的方式）开发的Agent智能体
4. 对于不了解的问题，坦诚说不知道并表示愿意学习
5. 保持回答长度适中，不要过长也不要过短"""


def handler(request):
    """Vercel Python Serverless Function handler"""
    if request.method == "OPTIONS":
        return Response(
            status=204,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            }
        )

    try:
        body = json.loads(request.body.decode("utf-8")) if request.body else {}
        messages = body.get("messages", [])
        session_id = body.get("session_id", "default")

        last_msg = messages[-1]["content"] if messages else ""
        if not last_msg:
            return Response(
                body=json.dumps({"response": "你好！我是候选人的AI代理 "}),
                headers={"Content-Type": "application/json"}
            )

        # 构建发送给大模型的消息
        llm_messages = [
            {"role": "system", "content": CANDIDATE_PROFILE},
            {"role": "user", "content": last_msg}
        ]

        # 调用阿里云百炼（通义千问）
        from openai import OpenAI
        client = OpenAI(
            api_key=os.getenv("BAILIAN_API_KEY", ""),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )

        response = client.chat.completions.create(
            model="qwen-max",
            messages=llm_messages,
            temperature=0.7,
        )

        result = response.choices[0].message.content

        return Response(
            body=json.dumps({"response": result}),
            headers={
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            }
        )

    except Exception as e:
        return Response(
            body=json.dumps({"response": f"抱歉，出错了：{str(e)}"}),
            status=500,
            headers={
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            }
        )


class Response:
    def __init__(self, body="", status=200, headers=None):
        self.body = body
        self.status = status
        self.headers = headers or {}
