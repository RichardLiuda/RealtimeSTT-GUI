# 🎙️ RealtimeSTT - 实时语音转写工具

一个基于 [RealtimeSTT](https://github.com/KoljaB/RealtimeSTT) 的 GUI 实现，提供多语言语音识别和实时翻译功能。本项目为原项目添加了图形界面、实时翻译和日志记录等功能。

## ✨ 主要特点

- 🔄 实时语音转写（基于 RealtimeSTT 引擎）
- 🌐 多语言支持（中文、英语、日语等）
- 🤖 自动翻译功能（基于百度翻译 API）
- 💻 GPU 加速支持
- 📝 自动保存转写记录（Markdown 格式）
- 🎯 用户友好的图形界面

## 🚀 快速开始

### 环境要求

```bash
Python 3.8+
PyQt5
RealtimeSTT
requests
```

### 安装依赖

```bash
pip install PyQt5 RealtimeSTT requests
```

### 运行程序

```bash
python realtime_stt_gui.py
```

## 🛠️ 配置说明

- 支持选择不同的语音识别模型（tiny/base/small/medium/large）
- 可调整语音检测灵敏度和静音检测时长
- 支持 GPU 加速和精度设置
- 实时转写和完整转写双模式

## 📝 日志记录

- 自动生成带时间戳的转写记录
- Markdown 格式便于阅读和分享
- 支持实时翻译结果记录

## 🔑 翻译功能配置

使用前需要配置百度翻译 API：
1. 在百度翻译开放平台注册账号
2. 获取 API ID 和密钥
3. 在 `realtime_stt_gui.py` 中更新配置：
```python
BAIDU_APPID = "你的APPID"
BAIDU_KEY = "你的密钥"
```

## 📚 相关项目

- [RealtimeSTT](https://github.com/KoljaB/RealtimeSTT) - 原始项目，提供底层的语音识别功能
- 作者：Kolja Beigel 
