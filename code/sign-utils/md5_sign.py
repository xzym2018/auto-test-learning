# -*- coding: utf-8 -*-
"""
MD5 请求签名工具
================
规则（常见约定）：SECRET + sorted(key=value&key=value...) → MD5 十六进制
- 参数按键名排序后拼接，保证客户端/服务端计算顺序一致
- sign 字段本身不参与签名（自引用）
"""
import hashlib


def md5_sign(params, secret):
    """对参数字典生成签名。"""
    pairs = sorted(f"{k}={v}" for k, v in params.items() if k != "sign")
    raw = secret + "&".join(pairs)
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


if __name__ == "__main__":
    # 自测示例：离线可跑，验证算法行为
    demo_secret = "demo_secret_do_not_use_in_prod"
    demo_params = {"b": "2", "a": "1", "c": "3"}
    sig = md5_sign(demo_params, demo_secret)
    print(f"params={demo_params}")
    print(f"sign={sig}")

    # 键序不影响结果
    assert md5_sign({"c": "3", "a": "1", "b": "2"}, demo_secret) == sig
    # sign 字段不参与签名
    assert md5_sign({**demo_params, "sign": "xxx"}, demo_secret) == sig
    print("OK: 键序无关、sign 字段已排除")
