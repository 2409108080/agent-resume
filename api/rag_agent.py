"""RAG Agent for Candidate Profile Retrieval"""

import os
import json
import hashlib
import requests
from typing import List, Dict, Any, Optional


class AlibabaEmbeddings:
    """使用阿里云百炼 API 进行文本嵌入"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """批量嵌入文档"""
        embedding_list = []
        for text in texts:
            resp = requests.post(
                "https://dashscope.aliyuncs.com/api/v1/services/embeddings/embeddings",
                headers=self.headers,
                json={
                    "model": "text-embedding-v3",
                    "input": {"texts": [text]},
                    "encoding_format": "float"
                }
            )
            if resp.status_code == 200:
                data = resp.json()
                emb = data["output"]["embeddings"][0]["embedding"]
                embedding_list.append(emb)
            else:
                raise Exception(f"Embedding failed: {resp.text}")
        return embedding_list

    def embed_query(self, text: str) -> List[float]:
        """单个查询嵌入"""
        return self.embed_documents([text])[0]


class SimpleVectorStore:
    """轻量级内存向量存储（基于余弦相似度）"""

    def __init__(self):
        self.ids: List[str] = []
        self.documents: List[str] = []
        self.embeddings: List[List[float]] = []
        self.metadatas: List[Dict[str, Any]] = []

    def add_texts_with_metadata(
        self,
        texts: List[str],
        metadatas: List[Dict[str, Any]],
        embeddings: Optional[List[List[float]]] = None
    ) -> None:
        """添加带元数据和预计算向量的文本"""
        for i, (text, meta) in enumerate(zip(texts, metadatas)):
            if not text.strip():
                continue
            text_id = hashlib.md5(text.encode()).hexdigest()[:8]
            self.ids.append(text_id)
            self.documents.append(text)
            self.metadatas.append(meta)
            # 使用预计算的向量或临时生成
            if embeddings and i < len(embeddings):
                self.embeddings.append(embeddings[i])
            else:
                self.embeddings.append(self._local_embed(text))
            meta["id"] = text_id

    def _local_embed(self, text: str) -> List[float]:
        """本地简单嵌入（fallback 方案）"""
        words = text.split()
        vocab = set(words)
        vec_size = 64
        vec = [0.0] * vec_size
        for w in vocab:
            h = int(hashlib.md5(w.encode()).hexdigest(), 16) % vec_size
            vec[h] += 1.0
        norm = (sum(v*v for v in vec)) ** 0.5
        return [v/norm for v in vec] if norm > 0 else vec

    def cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """计算余弦相似度"""
        dot_product = sum(x * y for x, y in zip(a, b))
        return dot_product

    def similarity_search(self, query_embedding: List[float], k: int = 3) -> List[Dict]:
        """检索 Top-K 相似文档"""
        scores = [
            self.cosine_similarity(query_embedding, emb)
            for emb in self.embeddings
        ]
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]

        results = []
        for idx in top_indices:
            results.append({
                "id": self.ids[idx],
                "content": self.documents[idx],
                "metadata": dict(self.metadatas[idx]),
                "score": scores[idx]
            })
        return results

    def get_source_doc_name(self, doc_idx: int) -> str:
        """根据索引获取源片段名称"""
        metadata = self.metadatas[doc_idx]
        return metadata.get("source", metadata.get("id", "unknown"))


# ============================================================================
# 候选人资料片段定义（按主题拆分，每个 ~200~400 tokens）
# ============================================================================

CANDIDATE_FRAGMENTS = {
    "basic_info": """基本信息：
- 姓名：张文远
- 年龄：26 岁
- 前端开发经验：5 年
- 求职方向：前端开发工程师，专注企业级应用开发
- 期望城市：沈阳
- 学历：东北农业大学大专，计算机科学与技术专业，2020-2022 年毕业""",

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
- 相关技术资产被甲方采纳为标准工具并持续使用
- 脚本和工具已被甲方正式采纳为标准化流程的一部分""",

    "project_others": """SDDC Automation（企业级私有云管理平台）项目：
- 参与前端从 0 到 1 的架构和工程化建设
- 参与和负责 RBAC 权限体系设计与落地，覆盖菜单、按钮、部门和数据范围
- 实现虚拟机全生命周期相关功能
- 参与远程控制台、运维监控、ECharts 可视化开发
- 沉淀公共组件和业务组件库

360PM（碧桂园工程管理平台）项目：
- 工程文档中心、多级文件管理、大文件上传、在线预览功能
- 数据可视化首页开发

联通行政办公平台项目：
- PC + H5 + APP 内嵌多端开发
- 多端数据同步和兼容处理
- 后期担任前端小组长""",

    "answer_rules": """回答规则和行为准则：

【回答长度】
- 默认回答 80～180 字，普通问题 2～4 句话
- 只有明确要求详细解释时才展开
- 第一轮回答简洁，追问后再深入

【项目问题回答结构】
- 项目是什么
- 我负责什么
- 1～2 个重点
- 结果/成效

【技术问题回答策略】
- 优先结合真实项目回答，特别是 Vue、Cypress、工程化、RBAC
- 严格区分"做过"、"参与过"、"了解但没实践"
- 如果资料没有明确说明实现方式，不要自行补充底层细节

【AI 项目相关】
- 只介绍实际实现的内容
- 不虚构高级 Agent 能力（如 RAG、Tool Calling、LangChain 等未实际使用）
- 近期通过 vibecoding 独立实践 AI 应用开发
- 实际使用 Prompt 设计、对话上下文管理、LLM API 调用
- 当前使用阿里云百炼 API + Vercel Serverless

【语气和表达】
- 像真实的 5 年前端工程师，自然、自信、简洁
- 不使用机械化自我弱化表达（如"这个很简单"、"我只是学习"、"经验不足"等）
- 对不会或未实践的技术，直接说明目前没有实际实践，可简要解释基本原理
- 不要创造新的数字、效率指标或项目成果
- 不要把团队成果全部说成个人独立完成"""
}


class CandidateRAGAgent:
    """基于 RAG 的候选人面试代理"""

    def __init__(self, api_key: str):
        """初始化 RAG Agent

        Args:
            api_key: 阿里云百炼 API Key
        """
        self.api_key = api_key
        self.vector_store = SimpleVectorStore()
        self._embeddings_client = None
        self._init_vector_store()

    @property
    def embeddings_client(self):
        """懒加载获取嵌入客户端"""
        if self._embeddings_client is None and self.api_key:
            self._embeddings_client = AlibabaEmbeddings(self.api_key)
        return self._embeddings_client

    def _init_vector_store(self) -> None:
        """初始化向量数据库"""
        texts = list(CANDIDATE_FRAGMENTS.values())
        metadatas = [{"source": name} for name in CANDIDATE_FRAGMENTS.keys()]

        # 优先使用百炼 API 进行嵌入（如果有 API key）
        if self.embeddings_client:
            try:
                embeddings = self.embeddings_client.embed_documents(texts)
            except Exception:
                # Fallback: 使用本地嵌入
                embeddings = [self._local_embed(text) for text in texts]
        else:
            embeddings = [self._local_embed(text) for text in texts]

        # 将分片添加到向量存储
        self.vector_store.add_texts_with_metadata(texts, metadatas, embeddings)

    def _local_embed(self, text: str) -> List[float]:
        """本地简单嵌入（fallback 方案）"""
        words = text.split()
        vocab = set(words)
        vec_size = 64
        vec = [0.0] * vec_size
        for w in vocab:
            h = int(hashlib.md5(w.encode()).hexdigest(), 16) % vec_size
            vec[h] += 1.0
        norm = (sum(v*v for v in vec)) ** 0.5
        return [v/norm for v in vec] if norm > 0 else vec

    def retrieve_context(self, query: str, top_k: int = 2) -> str:
        """检索与问题相关的候选人居资料片段

        Args:
            query: 用户问题
            top_k: 返回最相关的 K 个片段

        Returns:
            拼接的相关片段内容
        """
        # 嵌入查询
        if self.embeddings_client:
            try:
                query_embedding = self.embeddings_client.embed_query(query)
            except Exception:
                query_embedding = self._local_embed(query)
        else:
            query_embedding = self._local_embed(query)

        # 检索相关文档
        docs = self.vector_store.similarity_search(query_embedding, k=top_k)

        # 构建上下文字符串
        context_parts = []
        for doc in docs:
            source = doc["metadata"].get("source", "unknown")
            content = doc["content"]
            score = doc["score"]
            context_parts.append(f"[{source}] (相似度:{score:.3f})\n{content}")

        return "\n\n".join(context_parts)

    def generate_response(
        self,
        user_query: str,
        chat_history: List[Dict[str, str]]
    ) -> str:
        """生成面试回答

        Args:
            user_query: 用户问题
            chat_history: 对话历史列表 [{"role": "user/assistant", "content": "..."}]

        Returns:
            生成的回答内容
        """
        # 检索相关上下文
        relevant_context = self.retrieve_context(user_query)

        # 构建精简 system prompt
        system_prompt = f"""你是张文远的 AI 面试代理，请以张文远本人身份，自然、专业、真实地回答面试官问题。所有内容必须基于以下参考信息，不得虚构。

【参考信息】
{relevant_context}

## 回答规则
- 默认回答 80～180 字，普通问题 2～4 句话
- 只有明确要求详细解释时才展开
- 项目问题先回答：项目是什么、我负责什么、1～2 个重点、结果
- 前端问题优先结合真实项目回答，特别是 Vue、Cypress、工程化、RBAC
- AI 项目问题只介绍实际实现，不虚构高级 Agent 能力
- 严格区分"做过"、"参与过"、"了解但没实践"
- 如果资料没有明确说明实现方式，不要自行补充底层细节
- 不要创造新的数字、效率指标或项目成果
- 不要把团队成果全部说成个人独立完成
- 第一轮回答简洁，追问后再深入
- 语气像真实的 5 年前端工程师，自然、自信、简洁
- 不使用机械化自我弱化表达
- 对不会或未实践的技术，直接说明目前没有实际实践
"""

        # 构建消息序列
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(chat_history)

        # 调用 LLM
        from openai import OpenAI
        client = OpenAI(
            api_key=os.getenv("BAILIAN_API_KEY", self.api_key),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )

        response = client.chat.completions.create(
            model="qwen3.5-flash-2026-02-23",
            messages=messages,
            temperature=0.5,
            max_tokens=350,
        )

        return response.choices[0].message.content
