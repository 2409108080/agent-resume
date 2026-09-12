from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage

app = FastAPI(title="AI Resume Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 候选人设定（在这里改） ====================
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


# ==================== 会话存储 ====================
conversations: dict[str, list] = {}


class MessageItem(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[MessageItem]
    session_id: str = "default"


class ChatResponse(BaseModel):
    response: str


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    session_id = request.session_id

    # 初始化会话历史
    if session_id not in conversations:
        conversations[session_id] = []

    # 拿到最后一个用户消息
    last_msg = request.messages[-1].content if request.messages else ""
    if not last_msg:
        return ChatResponse(response="你好！我是候选人的AI代理，你可以问我任何关于他技术能力和项目经验的问题 🤖")

    # 获取历史对话消息并转换为LangChain消息格式
    history = conversations[session_id]

    # 限制历史消息数量，避免token超限（保留最近10条消息）
    MAX_HISTORY_MESSAGES = 10
    if len(history) > MAX_HISTORY_MESSAGES:
        history = history[-MAX_HISTORY_MESSAGES:]

    langchain_messages = []

    for msg in history:
        if msg["role"] == "user":
            langchain_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            langchain_messages.append(AIMessage(content=msg["content"]))

    # 初始化 LLM（阿里云百炼，兼容 OpenAI API 格式）
    llm = ChatOpenAI(
        openai_api_key=os.getenv("BAILIAN_API_KEY", ""),
        openai_api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
        model="qwen3.8-max",
        temperature=0.7,
    )

    # 构建包含历史消息的prompt模板
    prompt = ChatPromptTemplate.from_messages([
        ("system", CANDIDATE_PROFILE),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ])

    chain = prompt | llm | StrOutputParser()

    # 调用LLM，传入历史消息和当前输入
    result = chain.invoke({
        "history": langchain_messages,
        "input": last_msg
    })

    # 保存对话历史
    conversations[session_id].append({"role": "user", "content": last_msg})
    conversations[session_id].append({"role": "assistant", "content": result})

    # 确保历史消息不超过限制
    if len(conversations[session_id]) > MAX_HISTORY_MESSAGES * 2:
        conversations[session_id] = conversations[session_id][-MAX_HISTORY_MESSAGES*2:]

    return ChatResponse(response=result)


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "AI Resume Agent"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
