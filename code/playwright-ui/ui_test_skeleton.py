# -*- coding: utf-8 -*-
"""
Playwright UI 自动化骨架
========================
与业务无关的可复用模块，提供：
- 登录（用户名/密码表单）
- 带重试的页面跳转（应对加载不稳定）
- 截图取证（全页）
- 用例结果记录 + JSON 落盘
- JS 兜底输入 / 点击（应对前端拦截、受控组件）

凭证只从环境变量读取。选择器/URL 为占位符，接入项目时替换。
"""
import json
import os
import time

from playwright.sync_api import sync_playwright

BASE = os.environ.get("UI_BASE_URL", "https://example.com")
USER = os.environ.get("UI_USER", "")
PASSWORD = os.environ.get("UI_PASSWORD", "")
OUTDIR = "test_evidence"
os.makedirs(OUTDIR, exist_ok=True)

results = []


def ss(page, name):
    """全页截图取证，返回文件路径。"""
    path = os.path.join(OUTDIR, f"{name}.png")
    page.screenshot(path=path, full_page=True)
    return path


def record(case_id, status, notes="", evidence=""):
    """登记用例结果。status: PASS / FAIL / SKIP / PASS-WARN。"""
    results.append({"id": case_id, "status": status, "notes": notes, "evidence": evidence})
    icon = {"PASS": "[v]", "FAIL": "[x]", "SKIP": "[-]", "PASS-WARN": "[?]"}.get(status, "[?]")
    print(f"  {icon} {case_id}: {notes}")


def login(page, url, user_placeholder, pass_placeholder, submit_text):
    """通用登录：按占位符填表单并提交，等待网络空闲。"""
    page.goto(url)
    page.get_by_placeholder(user_placeholder).fill(USER)
    page.get_by_placeholder(pass_placeholder).fill(PASSWORD)
    page.get_by_role("button", name=submit_text).click()
    page.wait_for_load_state("networkidle", timeout=15000)
    time.sleep(2)


def goto_with_retry(page, url, ready_selector, retries=3):
    """跳转并等待关键元素出现，失败重试。返回是否就绪。"""
    for _ in range(retries):
        try:
            page.goto(url)
            page.wait_for_load_state("networkidle", timeout=10000)
            time.sleep(2)
            if page.locator(ready_selector).first.is_visible():
                return True
        except Exception:
            time.sleep(2)
    return False


def fill_input_via_js(page, selector, value):
    """
    JS 兜底输入：直接设置 value 并派发 input 事件。
    用于前端框架受控组件（React/AntD 等）拦截原生输入的场景。
    """
    page.evaluate(
        """([sel, val]) => {
            const el = document.querySelector(sel);
            if (!el) return false;
            const setter = Object.getOwnPropertyDescriptor(
                window.HTMLInputElement.prototype, 'value').set;
            setter.call(el, val);
            el.dispatchEvent(new Event('input', {bubbles: true}));
            return true;
        }""",
        [selector, value],
    )
    time.sleep(0.5)


def click_via_js(page, selector, text_keyword=None):
    """
    JS 兜底点击：跳过 Playwright 的可操作性检查。
    text_keyword 给定时，在匹配元素中按文本过滤。
    """
    return page.evaluate(
        """([sel, kw]) => {
            const els = document.querySelectorAll(sel);
            for (const el of els) {
                if (el.offsetWidth === 0) continue;
                if (kw && !(el.textContent || '').includes(kw)) continue;
                el.click();
                return true;
            }
            return false;
        }""",
        [selector, text_keyword],
    )


def run_demo():
    """演示：记录一条 SKIP 用例并产出报告结构。接入项目时替换为真实流程。"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        record("DEMO-001", "SKIP", "骨架演示：替换 login/goto_with_retry 的参数后接入真实页面")
        browser.close()

    passed = [r for r in results if r["status"] == "PASS"]
    failed = [r for r in results if r["status"] == "FAIL"]
    print(f"\n总计: {len(results)}  通过: {len(passed)}  失败: {len(failed)}")
    with open("ui_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"结果: ui_test_results.json, 截图目录: {OUTDIR}/")


if __name__ == "__main__":
    run_demo()
