# adb-ui-automation: ADB UI 自动化骨架

## 适用场景

针对 Android 应用（如图库、内容列表、电商首页）的 UI 自动化测试。
场景特点：
- 需要遍历长列表（Gallery / RecyclerView）查找特定元素。
- 需要检测布局异常（错位、空位、重叠）。
- 只能使用 ADB 和 UI 层级（UIAutomator2），不依赖 Root 或私有数据库。

## 核心能力

| 模块 | 功能 |
|------|------|
| `AdbClient` | ADB 命令封装：设备连接、Shell 命令、截屏、滑动、点击、获取 UI Dump |
| `GalleryParser` | UI XML 解析：提取元素坐标、文本、判断是否"已完成"、检测行列错位 |
| `scroll_and_find_target` | 长列表自动翻页：模拟真实用户滑动，去重指纹，定位目标元素 |

## 快速开始

```bash
pip install -r requirements.txt  # 当前无额外依赖，仅需 python3

# 设置环境变量（可选，或直接修改脚本中的 DEFAULT_PACKAGE）
export APP_PACKAGE="com.example.gallery"
export APP_COMPONENT="com.example.gallery/.ui.SplashActivity"

python adb_gallery.py
```

## 设计亮点（来自纯色自动化实战）

1. **稳定性读取**：连续两次获取 UI Dump 进行指纹比对，确保列表已停止滚动。
2. **防误判**：
    - 滑到底部判定：连续 3 次滑动且 UI XML 无变化才停止。
    - 点击前校验：再次核对目标元素坐标，防止点击瞬间发生位移。
3. **证据留存**：
    - 每次关键步骤保存 UI Dump（`*.xml`）和截图（`*.png`）。
    - 生成结构化报告（`summary.json`）。

## 从源脚本中抽取的模式

- **ADB 通信层**：统一封装 `subprocess.run`，处理编码和错误。
- **XML 解析**：使用正则提取 `bounds="[x,y][w,h]"` 并转为 `BBox` 对象。
- **长列表遍历**：维护 `seen_fingerprints` 集合，避免重复计数。

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `APP_PACKAGE` | 应用包名 | `com.example.gallery` |
| `APP_COMPONENT` | 启动 Activity | `{APP_PACKAGE}/.ui.SplashActivity` |
| `ADB_PATH` | ADB 可执行文件路径 | `adb` |

## 踩坑提示

- **UI Dump 权限**：部分应用在前台时 `uiautomator dump` 可能失败，需先清理后台或等待页面稳定。
- **坐标漂移**：动画过程中坐标是不稳定的，每次操作前需重新 `dump_ui`。
- **列表惯性**：滑动后需等待（建议 0.5s-1s）让列表惯性停止，否则读取的坐标是错的。
