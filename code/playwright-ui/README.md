# playwright-ui：UI 自动化骨架

## 适用场景

管理后台 / Web 页面的 UI 回归：登录、表单、列表、弹窗等操作验证 + 截图取证。

## 快速开始

```bash
pip install playwright
playwright install chromium
python ui_test_skeleton.py   # 演示模式，无需凭证
```

接入真实项目：

```bash
set UI_BASE_URL=https://your-env.example.com
set UI_USER=your_account
set UI_PASSWORD=your_password
```

然后基于骨架函数编写用例流程，每个用例调用 `record()` 登记结果。

## 骨架函数

| 函数 | 用途 |
|------|------|
| `login()` | 按占位符填登录表单并提交 |
| `goto_with_retry()` | 跳转 + 等待关键元素，失败重试 |
| `ss()` | 全页截图取证 |
| `record()` | 用例登记（PASS/FAIL/SKIP/PASS-WARN） |
| `fill_input_via_js()` | JS 兜底输入，应对受控组件 |
| `click_via_js()` | JS 兜底点击，跳过可操作性检查 |

## 踩坑提示

- **Ant Design 受控输入框**：Playwright 的 `fill()` 可能触发不了 onChange，用 `fill_input_via_js()` 走原生 setter + input 事件。
- **按钮文本带空格**：如 `保 存`，用 `text_keyword` 模糊匹配（`保` + `存` 都包含）更稳。
- **弹窗/抽屉遮罩拦截点击**：先 `click_via_js()` 兜底，不行再考虑 `force=True`。
- **headless 与有头差异**：元素可见性判断在两种模式下可能不同，失败时先用有头模式排查。
