# -*- coding: utf-8 -*-
"""
通用接口测试客户端
==================
与业务无关的可复用模块，提供：
- Token 登录（自动适配多种响应结构）
- Session 会话保持 + 统一请求头
- GET / POST / PUT / DELETE 统一封装，返回 (status_code, body)
- 响应自动解包（{"data": ...} 结构取 data）

凭证只从环境变量读取，不落盘、不入库。用法见 test_example.py。
"""
import os

import requests

requests.packages.urllib3.disable_warnings()


def require_env(name):
    """读取必需的环境变量，缺失时给出明确报错。"""
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"请设置环境变量 {name}")
    return value


class ApiClient:
    """带鉴权的接口测试客户端。"""

    def __init__(self, base_url, timeout=30, verify_ssl=False):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.verify = verify_ssl
        self.session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json",
        })

    def login(self, login_path, user_env, pass_env, source=None):
        """
        登录并把 Token 写入 Session 头。
        适配三种常见响应：{"token": ...} / {"data": {"token": ...}} / {"data": "..."}
        """
        payload = {
            "username": require_env(user_env),
            "password": require_env(pass_env),
        }
        if source:
            payload["source"] = source

        resp = self.session.post(
            f"{self.base_url}{login_path}", json=payload, timeout=15
        )
        body = resp.json()
        token = body.get("token") or body.get("data", {}).get("token", "")
        if not token:
            raise RuntimeError(f"登录响应中未找到 token: {str(body)[:200]}")

        self.session.headers.update({"Authorization": f"Token {token}"})
        return token

    def request(self, method, path, data=None):
        """
        统一请求封装。
        - GET:    data 作为 query params
        - DELETE: data 作为 query params（多数后端约定）
        - 其他:   data 作为 JSON body
        返回 (http_status, body)；网络异常返回 (-1, error_msg)。
        """
        url = f"{self.base_url}{path}"
        try:
            if method in ("GET", "DELETE"):
                r = self.session.request(method, url, params=data, timeout=self.timeout)
            else:
                r = self.session.request(method, url, json=data, timeout=self.timeout)
            try:
                body = r.json()
            except ValueError:
                return r.status_code, r.text[:200]
            # 常见包装结构自动解包
            if isinstance(body, dict) and set(body.keys()) <= {"code", "message", "data"}:
                return r.status_code, body.get("data")
            if isinstance(body, dict) and "data" in body:
                return r.status_code, body["data"]
            return r.status_code, body
        except Exception as e:
            return -1, str(e)[:200]
