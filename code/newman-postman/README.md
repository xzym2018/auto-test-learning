# newman-postman：Postman Collection 定时执行

## 适用场景

已有 Postman 调试好的接口集合，想低成本变成每日自动跑的回归任务，不想先上代码框架。

## 文件说明

| 文件 | 用途 |
|------|------|
| `collection.example.json` | 变量化模板：`{{base_url}}`、`{{token}}`，真实值绝不入库 |
| `run_newman.bat` | 批量执行同目录所有 collection，日志按日期落盘 |

## 使用方式

```bash
npm install -g newman
# 1. 从 Postman 导出 Collection 到本目录（确认已变量化，无硬编码 token）
# 2. 双击 run_newman.bat，或接入 Windows 计划任务
```

配合 Environment 使用：

```bash
newman run xxx.postman_collection.json -e env.postman_environment.json
```

## 关键实践

- **变量化一切环境相关值**：`{{base_url}}`、`{{token}}`、`{{user_id}}`，Collection 本身可安全入库。
- **日志按日期命名**：`newman_run_20260915.log`，便于追溯每天的执行结果。
- **退出码接入告警**：newman 失败时 `%errorlevel%` 非零，可接邮件/IM 通知。
- **升级路径**：Collection 规模变大后，迁移到 [../api-testing/](../api-testing/) 的代码化骨架。
