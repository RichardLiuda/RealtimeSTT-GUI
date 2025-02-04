# 🎙️ RealtimeSTT - 实时语音转写工具

一个基于 [RealtimeSTT](https://github.com/KoljaB/RealtimeSTT) 的 GUI 实现，提供多语言语音识别和实时翻译功能。本项目为原项目添加了图形界面、实时翻译和日志记录等功能。

## ✨ 主要特点

- 🔄 实时语音转写（基于 RealtimeSTT 引擎）
- 🌐 多语言支持（中文、英语、日语等）
- 🤖 自动翻译功能（基于百度翻译 API）
- 💻 GPU 加速支持
- 📝 自动保存转写记录（Markdown 格式）
- 🎯 用户友好的图形界面
- 🈁 日语汉字注音功能（自动添加平假名注音）

## 🚀 快速开始

### 环境要求

```bash
Python 3.8+
PyQt5
RealtimeSTT
requests
pykakasi  # 用于日语注音功能
```

### 安装依赖

```bash
pip install PyQt5 RealtimeSTT requests pykakasi
```

### 运行程序

```bash
python realtime_stt_gui.py
```

## 🛠️ 配置说明

### 语音识别配置
- 支持选择不同的语音识别模型（tiny/base/small/medium/large）
- 可调整语音检测灵敏度和静音检测时长
- 支持 GPU 加速和精度设置
- 实时转写和完整转写双模式

### 翻译配置
- 支持配置百度翻译 API 密钥
- 可在配置页面中设置翻译服务参数
- 支持启用/禁用自动翻译功能
- 可选择目标翻译语言

## 📝 日志记录

- 自动生成带时间戳的转写记录
- Markdown 格式便于阅读和分享
- 支持实时翻译结果记录
- 日语转写支持汉字注音（蓝色显示）
- 所有记录保存在同一个文件中（transcript.md）

### 日语注音功能
- 自动为日语转写中的汉字添加平假名注音
- 带注音的汉字以蓝色显示，提高可读性
- 注音格式：漢字(かんじ)
- 仅在选择日语语言时启用

## 🔑 功能配置

在程序的配置页面中可以设置：

1. 语音检测参数
   - Silero 灵敏度
   - 静音检测时长
   - 最小录音长度

2. 性能参数
   - Beam Size
   - 实时处理间隔
   - GPU 加速选项
   - 计算精度

3. 翻译参数
   - 百度翻译 API ID
   - 百度翻译密钥
   - 启用/禁用翻译
   - 目标语言选择

## 📚 相关项目

- [RealtimeSTT](https://github.com/KoljaB/RealtimeSTT) - 原始项目，提供底层的语音识别功能
- 作者：Kolja Beigel 
