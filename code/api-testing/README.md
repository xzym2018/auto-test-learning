# api-testing：通用接口测试骨架

## 适用场景

需要对 HTTP 接口做自动化回归（CRUD、异常边界、契约校验），又不想引入重型框架时，复制本目录即可开工。

## 模块组成

| 文件 | 职责 | 是否需改 |
|------|------|---------|
| `api_client.py` | 登录鉴权、Session、统一请求封装、响应解包 | 一般不改 |
| `recorder.py` | 用例登记、实时打印、汇总、JSON 落盘 | 一般不改 |
| `test_example.py` | 用法演示（跑通即说明骨架可用） | 换成真实用例 |
| `.env.example` | 环境变量模板 | 复制为 `.env` 填值 |

## 快速接入新项目

```bash
pip install requests
cp .env.example .env   # 填入测试环境账号
python test_example.py # 验证骨架（使用公开占位服务，无需 .env）
```

然后新建自己的用例文件：

```python
from api_client import ApiClient
from recorder import ResultRecorder

client = ApiClient("https://your-env.example.com")
client.login("/api/common/login/", "CMS_USER", "CMS_PASSWORD")  # 需要鉴权时
rec = ResultRecorder()

s, d = client.request("GET", "/api/your/resource/")
rec.record("API-001", "资源列表", "GET", "/api/your/resource/", s, 200, s == 200)

failed = rec.summary()
rec.save("results.json")
raise SystemExit(1 if failed else 0)  # 非零退出码供 CI 判断
```

## 设计要点（为什么这么写）

- **统一返回 `(status, body)`**：断言时不用关心异常，网络错误返回 `-1`，与 HTTP 状态码区分开。
- **DELETE 用 query params**：多数后端框架对 DELETE body 支持不一致，params 更通用。
- **响应自动解包 `data`**：减少每层用例的样板代码；不解包外层包装时注释掉即可。
- **退出码 = 失败数**：`SystemExit(1)` 让 Jenkins/流水线能直接判定失败，无需解析报告。
- **凭证只走环境变量**：代码可公开入库，`.env` 本地私有。

## 常见扩展

- 并发执行：用例间无依赖时，把 `client.request` 丢进 `concurrent.futures.ThreadPoolExecutor`
- 数据驱动：用例参数放 JSON/CSV，循环调用 `rec.record`
- 报告美化：`recorder.save()` 的 JSON 可自行渲染为 HTML，或换 pytest + allure
