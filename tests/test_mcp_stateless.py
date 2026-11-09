"""MCP Streamable HTTP 传输必须是**无状态**的。

背景(2026-11-05 线上故障):服务端默认的有状态会话只存在进程内存里,
容器一重启,客户端拿着旧的 Mcp-Session-Id 继续请求就会收到
`-32600 Session not found`。本项目的十个工具都不接收 Context,不使用
sampling / elicitation / 进度通知 / 资源订阅,分页游标也是 HMAC 自包含的,
所以会话不承载任何业务语义,应当关闭。

这些测试直接打 ASGI 传输层,而不是 `fastmcp.Client` 的内存传输——
后者根本不会产生 Mcp-Session-Id,测不到线上故障的那条路径。
"""
import json
import unittest

from fastapi.testclient import TestClient

import server

ACCEPT = {"Accept": "application/json, text/event-stream"}
INITIALIZE = {
    "jsonrpc": "2.0", "id": 1, "method": "initialize",
    "params": {"protocolVersion": "2025-06-18", "capabilities": {},
               "clientInfo": {"name": "stateless-test", "version": "1"}},
}


def _parse_sse(text: str) -> list[dict]:
    """从 text/event-stream 响应体里取出 JSON-RPC 消息。"""
    messages = []
    for line in text.splitlines():
        if line.startswith("data:"):
            messages.append(json.loads(line[5:].strip()))
    return messages


class StatelessHTTPTest(unittest.TestCase):
    def setUp(self):
        # path="/" 与 backend/main.py 的挂载方式一致;stateless_http 是本测试的对象。
        # FastMCP 的 StreamableHTTPSessionManager 需要父 app 跑它的 lifespan,
        # 生产方式见 backend/main.py 的 _lifespan,这里同样接上。
        self.mcp_app = server.mcp.http_app(path="/", stateless_http=True)
        from contextlib import asynccontextmanager
        from fastapi import FastAPI

        @asynccontextmanager
        async def lifespan(_app):
            async with self.mcp_app.lifespan(_app):
                yield

        outer = FastAPI(lifespan=lifespan)
        outer.mount("/", self.mcp_app)
        # TestClient 只有在上下文里才会真正跑 lifespan(触发 session manager 的 task group)。
        self.client = TestClient(outer)
        self.client.__enter__()
        self.addCleanup(self.client.__exit__, None, None, None)

    def _initialize(self):
        response = self.client.post("/", json=INITIALIZE, headers=ACCEPT)
        self.assertEqual(response.status_code, 200, response.text)
        return response

    def test_initialize_does_not_hand_out_session_id(self):
        """无状态模式不应分配会话标识。"""
        response = self._initialize()
        self.assertIsNone(response.headers.get("mcp-session-id"))
        messages = _parse_sse(response.text)
        self.assertEqual(messages[0]["id"], 1)
        self.assertEqual(messages[0]["result"]["serverInfo"]["name"], "pdf-rag")

    def test_repeated_initialize_all_succeed(self):
        """多次 initialize 都应成功——有状态模式会因会话互斥/超限出现失败。"""
        for _ in range(3):
            self._initialize()

    def test_stale_session_id_is_not_rejected(self):
        """核心回归:带任意旧 session id 的请求仍被正常处理。

        有状态模式下这里会返回 404 + `-32600 Session not found`,
        正是线上客户端报的错。
        """
        request = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
        response = self.client.post(
            "/", json=request,
            headers={**ACCEPT, "Mcp-Session-Id": "deadbeefdeadbeefdeadbeefdeadbeef"},
        )
        self.assertEqual(response.status_code, 200, response.text)
        messages = _parse_sse(response.text)
        self.assertEqual(messages[0]["id"], 2)
        self.assertIn("tools", messages[0]["result"])
        self.assertNotIn("error", messages[0])

    def test_tools_list_shape_unchanged(self):
        """无状态化不应改变工具契约:仍是 10 个工具,schema_version 语义不变。"""
        request = {"jsonrpc": "2.0", "id": 3, "method": "tools/list", "params": {}}
        response = self.client.post("/", json=request, headers=ACCEPT)
        tools = _parse_sse(response.text)[0]["result"]["tools"]
        self.assertEqual(len(tools), 10)
        names = {tool["name"] for tool in tools}
        self.assertIn("pdf_rag_search", names)
        search = next(tool for tool in tools if tool["name"] == "pdf_rag_search")
        properties = search["inputSchema"]["properties"]
        # structured 必须仍在 schema 里,且默认关闭
        self.assertIn("structured", properties)
        self.assertIs(properties["structured"].get("default"), False)


if __name__ == "__main__":
    unittest.main()
