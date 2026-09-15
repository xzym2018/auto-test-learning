# auto-test-learning

自动化测试个人知识库：**可复用代码** + **方法论沉淀** 为主体，每日打卡记录学习轨迹。

## 目录导航

| 目录 | 内容 | 说明 |
|------|------|------|
| [code/](code/) | 可复用代码骨架 | 与业务无关，copy 改配置即可用于新项目 |
| [methodology/](methodology/) | 方法论 | 从实战中提炼的通用方法，已脱敏 |
| [daily/](daily/) | 每日打卡 | 学习时间线，轻量记录 |

## code 货架速览

| 模块 | 解决的问题 | 技术栈 |
|------|-----------|--------|
| [api-testing](code/api-testing/) | 接口测试：登录鉴权、统一请求封装、断言统计、结果落盘 | requests |
| [sign-utils](code/sign-utils/) | 请求签名（SECRET + 排序键值对 → MD5） | hashlib |
| [playwright-ui](code/playwright-ui/) | UI 自动化：登录、截图取证、JS 兜底交互 | playwright |
| [newman-postman](code/newman-postman/) | Postman Collection 定时执行 + 日志 | newman |
| [adb-ui-automation](code/adb-ui-automation/) | Android UI 自动化：ADB 封装、图库列表遍历、布局错位检测 | python, adb |

## methodology 索引

- [接口自动化回归体系](methodology/接口自动化回归体系.md)：分层架构、测试矩阵、冒烟/回归分层
- [接口契约回归与兼容性测试](methodology/接口契约回归与兼容性测试.md)：契约断言、基线比对、风险分级
- [CI集成与质量门禁](methodology/CI集成与质量门禁.md)：Jenkins 流水线、门禁规则、结果映射

## 使用方式

1. 克隆后用 Obsidian「Open folder as vault」打开本目录（可选，纯 GitHub 也可读）
2. 复用代码：复制对应模块目录 → 按 README 改配置 → 跑示例验证
3. 每日学习：在 `daily/` 下按 `YYYY-MM/YYYY-MM-DD.md` 记录，链回相关代码/方法论

## 脱敏约定

本仓库不含任何真实环境地址、账号、密钥、业务数据。所有凭证通过环境变量注入，示例统一使用 `example.com` 占位。
