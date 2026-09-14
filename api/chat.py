import json
import os
from http.server import BaseHTTPRequestHandler


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

            # 使用 RAG Agent 生成回答
            from rag_agent import CandidateRAGAgent

            rag_agent = CandidateRAGAgent(api_key=os.getenv("BAILIAN_API_KEY", ""))

            # 转换消息格式（过滤掉 system 角色）
            chat_history = [
                {"role": m.get("role", "user"), "content": m.get("content", "")}
                for m in messages
                if m.get("role") in ("user", "assistant")
            ]

            result = rag_agent.generate_response(
                user_query=messages[-1]["content"],
                chat_history=chat_history
            )
            self._send_json({"response": result})

        except Exception as e:
            self._send_json({"response": f"抱歉，出错了：{str(e)}"}, status=500)
