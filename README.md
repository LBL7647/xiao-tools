# QuotaHUD

MIMO & DeepSeek API 额度悬浮监控工具 — 桌面悬浮窗实时查看 API 余额。

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

## 功能

- **实时监控** — 每 2 秒自动刷新 MIMO Token 用量和 DeepSeek 账户余额
- **双模式** — 展开模式（详细数据 + 进度条）和迷你模式（紧凑一行）
- **12 种主题** — Dark、Glass、Cyber、Purple、Ocean、Sunset 等，支持透明度调节
- **圆角磨砂** — Win32 DWM 圆角窗口 + 玻璃拟态风格
- **全局快捷键** — 一键显示/隐藏（默认 Ctrl+Alt+Q，可自定义）
- **置顶悬浮** — 始终在最前，拖拽移动，不抢焦点
- **持久配置** — Cookie、API Key、主题、快捷键设置自动保存

## 快速开始

### 环境要求

- Windows 10 / 11
- Python 3.8+

### 安装依赖

```bash
pip install customtkinter requests
```

### 配置

首次运行后，点击齿轮图标进入设置：

| 设置项 | 说明 |
|--------|------|
| MIMO Cookie | 从浏览器开发者工具获取 |
| DeepSeek Key | DeepSeek API 的 Bearer Token |
| 快捷键 | 显示/隐藏悬浮窗的全局热键 |

### 启动

```bash
# 方式一：双击 启动.bat
# 方式二：命令行
cd src
pythonw main.py
```

> 使用 `pythonw` 运行，不会弹出黑色命令行窗口。

## 项目结构

```
src/
├── main.py         # 入口
├── app.py          # 主界面（悬浮窗）
├── api.py          # MIMO / DeepSeek API 请求
├── config.py       # API 地址和默认配置
├── settings.py     # 持久化设置 + 设置面板
├── themes.py       # 12 种主题 + 主题选择器
├── hotkey.py       # Win32 全局热键
└── rounded.py      # Win32 DWM 圆角窗口
```

## License

MIT
