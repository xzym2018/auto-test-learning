# -*- coding: utf-8 -*-
"""
用法示例：用公开占位服务演示 ApiClient + ResultRecorder 的配合。
目标服务为 JSONPlaceholder（免费假 REST API，无需账号），换成真实项目时：
1. 修改 BASE / 路径
2. 需要鉴权时调用 client.login(...)
3. 断言逻辑按业务契约改写
"""
from api_client import ApiClient
from recorder import ResultRecorder

BASE = "https://jsonplaceholder.typicode.com"

client = ApiClient(BASE)
rec = ResultRecorder()

# --- 正常场景 ---
s, d = client.request("GET", "/posts/1")
rec.record("EX-001", "获取单条资源", "GET", "/posts/1", s, 200,
           s == 200 and isinstance(d, dict) and d.get("id") == 1)

s, d = client.request("GET", "/posts", {"userId": 1})
rec.record("EX-002", "列表+查询参数", "GET", "/posts", s, 200,
           s == 200 and isinstance(d, list) and len(d) > 0)

s, d = client.request("POST", "/posts", {"title": "demo", "body": "x", "userId": 1})
rec.record("EX-003", "创建资源", "POST", "/posts", s, 201,
           s == 201 and isinstance(d, dict) and d.get("id"))

# --- 异常场景 ---
s, d = client.request("GET", "/posts/999999")
rec.record("EX-004", "不存在资源(404)", "GET", "/posts/999999", s, 404, s == 404)

failed = rec.summary()
rec.save("example_results.json")
raise SystemExit(1 if failed else 0)
