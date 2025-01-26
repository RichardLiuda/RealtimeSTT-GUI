import sys
import os
import json
import hashlib
import random
import requests
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QPushButton, QTextEdit, QComboBox, QLabel,
                             QCheckBox, QHBoxLayout, QFrame, QDialog,
                             QTabWidget, QSpinBox, QDoubleSpinBox, QGridLayout,
                             QGroupBox, QLineEdit)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QColor
from RealtimeSTT import AudioToTextRecorder

# 创建日志文件夹
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# 百度翻译 API 配置
BAIDU_APPID = ""  # 替换为你的百度翻译 API ID
BAIDU_KEY = ""  # 替换为你的百度翻译密钥
BAIDU_API_URL = "https://fanyi-api.baidu.com/api/trans/vip/translate"


def translate_text(text, from_lang='en', to_lang='zh'):
    """使用百度翻译 API 翻译文本"""
    try:
        salt = str(random.randint(32768, 65536))
        sign = hashlib.md5(
            (BAIDU_APPID + text + salt + BAIDU_KEY).encode()).hexdigest()

        params = {
            'appid': BAIDU_APPID,
            'q': text,
            'from': from_lang,
            'to': to_lang,
            'salt': salt,
            'sign': sign
        }

        response = requests.get(BAIDU_API_URL, params=params)
        result = response.json()

        if 'trans_result' in result:
            return result['trans_result'][0]['dst']
        else:
            print(f"翻译错误: {result.get('error_msg', '未知错误')}")
            return None
    except Exception as e:
        print(f"翻译请求失败: {e}")
        return None


class TranscriptionThread(QThread):
    text_signal = pyqtSignal(str)
    realtime_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, model="tiny", enable_realtime=True):
        super().__init__()
        self.enable_realtime = enable_realtime
        self.recorder = None
        self.model = model
        self.is_recording = False
        self.language = None
        self.config = {
            'silero_sensitivity': 0.7,
            'post_speech_silence_duration': 0.5,
            'min_length_of_recording': 0.5,
            'beam_size': 3,
            'realtime_processing_pause': 0.2,
            'device': 'cuda',
            'compute_type': 'float16'
        }

    def setup_recorder(self):
        try:
            language_map = {
                '自动检测': None,
                '中文 (Chinese)': 'zh',
                '英语 (English)': 'en',
                '日语 (Japanese)': 'ja',
                '韩语 (Korean)': 'ko',
                '俄语 (Russian)': 'ru',
                '德语 (German)': 'de',
                '法语 (French)': 'fr',
                '西班牙语 (Spanish)': 'es'
            }

            self.recorder = AudioToTextRecorder(
                model=self.model,
                language=language_map.get(self.language),
                enable_realtime_transcription=self.enable_realtime,
                on_realtime_transcription_update=self.on_realtime_update
                if self.enable_realtime else None,
                silero_sensitivity=self.config['silero_sensitivity'],
                post_speech_silence_duration=self.
                config['post_speech_silence_duration'],
                min_length_of_recording=self.config['min_length_of_recording'],
                beam_size=self.config['beam_size'],
                realtime_processing_pause=self.
                config['realtime_processing_pause'],
                device=self.config['device'],
                compute_type=self.config['compute_type'])
        except Exception as e:
            print(f"录音器初始化错误: {e}")
            self.is_recording = False

    def on_realtime_update(self, text):
        if self.is_recording and text:
            self.realtime_signal.emit(text)

    def run(self):
        try:
            self.setup_recorder()
            while self.is_recording:
                if self.recorder:
                    text = self.recorder.text()
                    if text:
                        self.text_signal.emit(text)
                self.msleep(100)
        finally:
            self.cleanup()
            self.finished_signal.emit()

    def cleanup(self):
        try:
            if self.recorder:
                self.recorder.stop()
                self.recorder = None
        except Exception as e:
            print(f"清理录音器错误: {e}")

    def start_recording(self):
        self.is_recording = True
        self.start()

    def stop_recording(self):
        self.is_recording = False
        self.cleanup()
        self.wait(1000)


class MaterialButton(QPushButton):

    def __init__(self, text, color="#6750A4"):
        super().__init__(text)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 24px;
                padding: 12px 32px;
                font-size: 16px;
                font-weight: 500;
                min-width: 140px;
                min-height: 48px;
                margin: 8px;
            }}
            QPushButton:hover {{
                background-color: {self.adjust_color(color, 1.1)};
            }}
            QPushButton:pressed {{
                background-color: {self.adjust_color(color, 0.9)};
            }}
            QPushButton:disabled {{
                background-color: #CAC4D0;
                color: #1D1B20;
            }}
        """)

    @staticmethod
    def adjust_color(color, factor):
        c = QColor(color)
        h, s, v, a = c.getHsv()
        v = min(255, int(v * factor))
        c.setHsv(h, s, v, a)
        return c.name()


class ConfigDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("配置")
        self.setMinimumSize(700, 500)
        self.setup_style()
        self.setup_layout()

    def setup_style(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFBFE;
            }
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #E7E0EC;
                border-radius: 12px;
                margin-top: 16px;
                padding: 24px;
            }
            QGroupBox::title {
                color: #6750A4;
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }
            QSpinBox, QDoubleSpinBox {
                border: 2px solid #79747E;
                border-radius: 8px;
                padding: 8px;
                min-width: 120px;
                font-size: 14px;
            }
            QLabel {
                font-size: 14px;
                margin: 8px 0;
            }
        """)

    def setup_layout(self):
        layout = QVBoxLayout(self)
        tabs = QTabWidget()

        # 语音检测设置
        vad_tab = self.create_vad_tab()
        tabs.addTab(vad_tab, "语音检测")

        # 性能设置
        perf_tab = self.create_perf_tab()
        tabs.addTab(perf_tab, "性能设置")

        # 翻译设置
        trans_tab = self.create_trans_tab()
        tabs.addTab(trans_tab, "翻译设置")

        layout.addWidget(tabs)

        # 按钮
        button_layout = QHBoxLayout()
        save_button = MaterialButton("保存", "#6750A4")
        cancel_button = MaterialButton("取消", "#B4261E")

        save_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

    def create_vad_tab(self):
        tab = QWidget()
        layout = QGridLayout()
        group = QGroupBox("语音检测参数")
        grid = QGridLayout()

        # Silero灵敏度
        self.silero_sensitivity = QDoubleSpinBox()
        self.silero_sensitivity.setRange(0, 1)
        self.silero_sensitivity.setSingleStep(0.1)
        self.silero_sensitivity.setValue(0.7)
        grid.addWidget(QLabel("Silero灵敏度:"), 0, 0)
        grid.addWidget(self.silero_sensitivity, 0, 1)

        # 静音检测时长
        self.silence_duration = QDoubleSpinBox()
        self.silence_duration.setRange(0.1, 2.0)
        self.silence_duration.setSingleStep(0.1)
        self.silence_duration.setValue(0.5)
        grid.addWidget(QLabel("静音检测时长(秒):"), 1, 0)
        grid.addWidget(self.silence_duration, 1, 1)

        # 最小录音长度
        self.min_recording = QDoubleSpinBox()
        self.min_recording.setRange(0.1, 5.0)
        self.min_recording.setSingleStep(0.1)
        self.min_recording.setValue(0.5)
        grid.addWidget(QLabel("最小录音长度(秒):"), 2, 0)
        grid.addWidget(self.min_recording, 2, 1)

        group.setLayout(grid)
        layout.addWidget(group)
        tab.setLayout(layout)
        return tab

    def create_perf_tab(self):
        tab = QWidget()
        layout = QGridLayout()
        group = QGroupBox("性能参数")
        grid = QGridLayout()

        # Beam Size
        self.beam_size = QSpinBox()
        self.beam_size.setRange(1, 10)
        self.beam_size.setValue(3)
        grid.addWidget(QLabel("Beam Size:"), 0, 0)
        grid.addWidget(self.beam_size, 0, 1)

        # 实时处理间隔
        self.processing_pause = QDoubleSpinBox()
        self.processing_pause.setRange(0.1, 1.0)
        self.processing_pause.setSingleStep(0.1)
        self.processing_pause.setValue(0.2)
        grid.addWidget(QLabel("实时处理间隔(秒):"), 1, 0)
        grid.addWidget(self.processing_pause, 1, 1)

        # GPU 加速选项
        self.device_combo = QComboBox()
        self.device_combo.addItems(["cuda", "cpu"])
        grid.addWidget(QLabel("计算设备:"), 2, 0)
        grid.addWidget(self.device_combo, 2, 1)

        # 计算精度选项
        self.compute_type_combo = QComboBox()
        self.compute_type_combo.addItems(["float16", "float32"])
        grid.addWidget(QLabel("计算精度:"), 3, 0)
        grid.addWidget(self.compute_type_combo, 3, 1)

        # 当设备切换时自动调整精度
        def on_device_changed(device):
            if device == "cpu":
                self.compute_type_combo.setCurrentText("float32")
                self.compute_type_combo.setEnabled(False)
            else:
                self.compute_type_combo.setEnabled(True)

        self.device_combo.currentTextChanged.connect(on_device_changed)
        # 初始化时检查一次
        on_device_changed(self.device_combo.currentText())

        group.setLayout(grid)
        layout.addWidget(group)
        tab.setLayout(layout)
        return tab

    def create_trans_tab(self):
        tab = QWidget()
        layout = QGridLayout()
        group = QGroupBox("翻译参数")
        grid = QGridLayout()

        # 启用翻译
        self.enable_trans = QCheckBox("启用翻译")
        self.enable_trans.setChecked(True)
        grid.addWidget(self.enable_trans, 0, 0, 1, 2)

        # 百度翻译 API ID
        self.baidu_appid = QLineEdit()
        self.baidu_appid.setPlaceholderText("请输入百度翻译 API ID")
        grid.addWidget(QLabel("API ID:"), 1, 0)
        grid.addWidget(self.baidu_appid, 1, 1)

        # 百度翻译密钥
        self.baidu_key = QLineEdit()
        self.baidu_key.setPlaceholderText("请输入百度翻译密钥")
        self.baidu_key.setEchoMode(QLineEdit.Password)
        grid.addWidget(QLabel("密钥:"), 2, 0)
        grid.addWidget(self.baidu_key, 2, 1)

        # 目标语言
        self.target_lang = QComboBox()
        self.target_lang.addItems(
            ["中文", "英语", "日语", "韩语", "俄语", "德语", "法语", "西班牙语"])
        grid.addWidget(QLabel("目标语言:"), 3, 0)
        grid.addWidget(self.target_lang, 3, 1)

        group.setLayout(grid)
        layout.addWidget(group)
        tab.setLayout(layout)
        return tab

    def get_config(self):
        return {
            'silero_sensitivity': self.silero_sensitivity.value(),
            'post_speech_silence_duration': self.silence_duration.value(),
            'min_length_of_recording': self.min_recording.value(),
            'beam_size': self.beam_size.value(),
            'realtime_processing_pause': self.processing_pause.value(),
            'device': self.device_combo.currentText(),
            'compute_type': self.compute_type_combo.currentText(),
            'enable_translation': self.enable_trans.isChecked(),
            'baidu_appid': self.baidu_appid.text(),
            'baidu_key': self.baidu_key.text(),
            'target_language': self.target_lang.currentText()
        }


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.init_log_file()
        self.current_realtime_text = ""  # 用于临时存储实时转写文本

    def init_ui(self):
        self.setWindowTitle("实时语音转文字")
        self.setMinimumSize(800, 600)
        self.init_config()
        self.setup_style()
        self.setup_layout()
        self.setup_signals()

    def init_config(self):
        # 检测系统是否支持 CUDA
        import torch
        default_device = 'cuda' if torch.cuda.is_available() else 'cpu'
        default_compute_type = 'float16' if default_device == 'cuda' else 'float32'

        self.config = {
            'silero_sensitivity': 0.7,
            'post_speech_silence_duration': 0.5,
            'min_length_of_recording': 0.5,
            'beam_size': 3,
            'realtime_processing_pause': 0.2,
            'device': default_device,
            'compute_type': default_compute_type,
            'enable_translation': True,
            'baidu_appid': BAIDU_APPID,
            'baidu_key': BAIDU_KEY,
            'target_language': '中文'
        }
        self.transcription_thread = None

    def init_log_file(self):
        try:
            # 创建新的日志文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.log_file = os.path.join(LOG_DIR, f"transcript_{timestamp}.md")
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 写入日志文件头部
            with open(self.log_file, "w", encoding="utf-8") as f:
                f.write("# 🎙️ 语音转写记录\n\n")
                f.write("## 📝 会话信息\n\n")
                f.write(f"- 📅 **时间**：{current_time}\n")
                f.write(f"- 🤖 **模型**：`{self.model_combo.currentText()}`\n")
                f.write(f"- 🌐 **语言**：`{self.language_combo.currentText()}`\n")
                f.write(f"- ⚡ **设备**：`{self.config['device']}`\n")
                f.write(f"- 🎯 **精度**：`{self.config['compute_type']}`\n")
                f.write(f"- 🔄 **翻译**：启用\n\n")
                f.write("## ⚙️ 配置信息\n\n")
                f.write("### 🎤 语音检测\n\n")
                f.write(f"- 灵敏度：`{self.config['silero_sensitivity']}`\n")
                f.write(
                    f"- 静音检测：`{self.config['post_speech_silence_duration']}秒`\n"
                )
                f.write(
                    f"- 最小录音：`{self.config['min_length_of_recording']}秒`\n\n")
                f.write("### 🚀 性能参数\n\n")
                f.write(f"- Beam Size：`{self.config['beam_size']}`\n")
                f.write(
                    f"- 处理间隔：`{self.config['realtime_processing_pause']}秒`\n\n"
                )
                f.write("## 📄 转写内容\n\n")
        except Exception as e:
            print(f"创建日志文件失败: {e}")

    def setup_style(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #FFFBFE;
            }
            QLabel {
                font-size: 16px;
                color: #1D1B20;
                margin: 8px 0;
            }
            QComboBox {
                border: 2px solid #79747E;
                border-radius: 12px;
                padding: 8px 16px;
                min-width: 200px;
                font-size: 16px;
                background-color: white;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 20px;
            }
            QTextEdit {
                border: 2px solid #E7E0EC;
                border-radius: 16px;
                padding: 16px;
                font-size: 16px;
                line-height: 1.5;
                background-color: white;
            }
            QCheckBox {
                font-size: 16px;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 24px;
                height: 24px;
                border: 2px solid #79747E;
                border-radius: 4px;
            }
            QCheckBox::indicator:checked {
                background-color: #6750A4;
                border-color: #6750A4;
            }
        """)

    def setup_layout(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(24, 24, 24, 24)

        # 顶部卡片
        top_card = self.create_top_card()
        main_layout.addWidget(top_card)

        # 内容卡片
        content_card = self.create_content_card()
        main_layout.addWidget(content_card)

    def create_top_card(self):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #E7E0EC;
                border-radius: 16px;
            }
        """)
        layout = QVBoxLayout(card)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # 模型选择
        model_layout = QHBoxLayout()
        model_label = QLabel("选择模型:")
        self.model_combo = QComboBox()
        self.model_combo.addItems(["tiny", "base", "small", "medium", "large"])
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_combo)
        model_layout.addStretch()
        layout.addLayout(model_layout)

        # 语言选择
        language_layout = QHBoxLayout()
        language_label = QLabel("选择语言:")
        self.language_combo = QComboBox()
        self.language_combo.addItems([
            "自动检测", "中文 (Chinese)", "英语 (English)", "日语 (Japanese)",
            "韩语 (Korean)", "俄语 (Russian)", "德语 (German)", "法语 (French)",
            "西班牙语 (Spanish)"
        ])
        language_layout.addWidget(language_label)
        language_layout.addWidget(self.language_combo)
        language_layout.addStretch()
        layout.addLayout(language_layout)

        # 实时转写选项（默认开启）
        self.realtime_checkbox = QCheckBox("启用实时转写")
        self.realtime_checkbox.setChecked(True)  # 默认选中
        layout.addWidget(self.realtime_checkbox)

        # 按钮
        button_layout = QHBoxLayout()
        self.record_button = MaterialButton("开始录音", "#6750A4")
        self.config_button = MaterialButton("配置", "#79747E")
        button_layout.addWidget(self.record_button)
        button_layout.addWidget(self.config_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        return card

    def create_content_card(self):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #E7E0EC;
                border-radius: 16px;
            }
        """)
        layout = QVBoxLayout(card)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # 实时转写显示
        realtime_label = QLabel("实时转写:")
        self.realtime_text = QTextEdit()
        self.realtime_text.setReadOnly(True)
        self.realtime_text.setMinimumHeight(100)
        layout.addWidget(realtime_label)
        layout.addWidget(self.realtime_text)

        # 完整转写显示
        complete_label = QLabel("完整转写:")
        self.complete_text = QTextEdit()
        self.complete_text.setReadOnly(True)
        self.complete_text.setMinimumHeight(200)
        layout.addWidget(complete_label)
        layout.addWidget(self.complete_text)

        return card

    def setup_signals(self):
        self.record_button.clicked.connect(self.toggle_recording)
        self.config_button.clicked.connect(self.show_config_dialog)

    def toggle_recording(self):
        if not self.transcription_thread or not self.transcription_thread.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        try:
            # 清空当前实时转写文本
            self.current_realtime_text = ""

            # 记录开始新的录音会话
            with open(self.log_file, "a", encoding="utf-8") as f:
                current_time = datetime.now().strftime("%H:%M:%S")
                f.write(f"\n### 🎬 录音开始 `{current_time}`\n\n")
        except Exception as e:
            print(f"写入日志失败: {e}")

        self.record_button.setText("停止录音")
        self.record_button.setStyleSheet(
            self.record_button.styleSheet().replace("#6750A4", "#B3261E"))
        self.model_combo.setEnabled(False)
        self.language_combo.setEnabled(False)
        self.realtime_checkbox.setEnabled(False)
        self.config_button.setEnabled(False)

        self.transcription_thread = TranscriptionThread(
            model=self.model_combo.currentText(),
            enable_realtime=self.realtime_checkbox.isChecked())
        self.transcription_thread.language = self.language_combo.currentText()
        self.transcription_thread.config = self.config
        self.transcription_thread.text_signal.connect(
            self.update_complete_text)
        self.transcription_thread.realtime_signal.connect(
            self.update_realtime_text)
        self.transcription_thread.finished_signal.connect(
            self.on_recording_finished)
        self.transcription_thread.start_recording()

    def stop_recording(self):
        if self.transcription_thread and self.transcription_thread.is_recording:
            self.transcription_thread.stop_recording()
            self.record_button.setEnabled(False)
            self.record_button.setText("正在停止...")

    def on_recording_finished(self):
        try:
            if self.current_realtime_text:  # 如果有未完成的实时转写，记录最后的结果
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(f"> {self.current_realtime_text}\n\n")

            # 添加结束标记和统计信息
            with open(self.log_file, "a", encoding="utf-8") as f:
                current_time = datetime.now().strftime("%H:%M:%S")
                f.write(f"\n### 🏁 录音结束 `{current_time}`\n\n")
                f.write("---\n\n")

            # 清空当前实时转写文本
            self.current_realtime_text = ""
        except Exception as e:
            print(f"写入会话结束信息失败: {e}")

        self.record_button.setEnabled(True)
        self.record_button.setText("开始录音")
        self.record_button.setStyleSheet(
            self.record_button.styleSheet().replace("#B3261E", "#6750A4"))
        self.model_combo.setEnabled(True)
        self.language_combo.setEnabled(True)
        self.realtime_checkbox.setEnabled(True)
        self.config_button.setEnabled(True)

    def update_realtime_text(self, text):
        if text:
            try:
                # 更新界面显示
                self.realtime_text.setText(text)
                self.realtime_text.verticalScrollBar().setValue(
                    self.realtime_text.verticalScrollBar().maximum())

                # 更新当前实时转写文本
                self.current_realtime_text = text
            except Exception as e:
                print(f"更新实时文本失败: {e}")

    def update_complete_text(self, text):
        if text and text != self.current_realtime_text:  # 避免重复记录
            try:
                current_time = datetime.now().strftime("%H:%M:%S")
                formatted_text = f"[{current_time}] {text}\n"

                # 更新界面显示
                self.complete_text.append(formatted_text)
                self.complete_text.verticalScrollBar().setValue(
                    self.complete_text.verticalScrollBar().maximum())

                # 获取翻译
                translated_text = None
                if self.config[
                        'enable_translation'] and self.language_combo.currentText(
                        ) != "中文 (Chinese)":
                    from_lang = {
                        "英语 (English)": "en",
                        "日语 (Japanese)": "jp",
                        "韩语 (Korean)": "kor",
                        "俄语 (Russian)": "ru",
                        "德语 (German)": "de",
                        "法语 (French)": "fra",
                        "西班牙语 (Spanish)": "spa",
                        "自动检测": "auto"
                    }.get(self.language_combo.currentText(), "auto")

                    to_lang = {
                        "中文": "zh",
                        "英语": "en",
                        "日语": "jp",
                        "韩语": "kor",
                        "俄语": "ru",
                        "德语": "de",
                        "法语": "fra",
                        "西班牙语": "spa"
                    }.get(self.config['target_language'], "zh")

                    translated_text = translate_text(text,
                                                     from_lang=from_lang,
                                                     to_lang=to_lang)

                # 写入日志文件，添加缩进和引用格式
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(f"> {text}\n")
                    if translated_text:
                        f.write(f"> 🔄 译文：{translated_text}\n")
                    f.write("\n")

            except Exception as e:
                print(f"更新完整文本失败: {e}")

    def show_config_dialog(self):
        dialog = ConfigDialog(self)
        dialog.silero_sensitivity.setValue(self.config['silero_sensitivity'])
        dialog.silence_duration.setValue(
            self.config['post_speech_silence_duration'])
        dialog.min_recording.setValue(self.config['min_length_of_recording'])
        dialog.beam_size.setValue(self.config['beam_size'])
        dialog.processing_pause.setValue(
            self.config['realtime_processing_pause'])
        dialog.device_combo.setCurrentText(self.config['device'])
        dialog.compute_type_combo.setCurrentText(self.config['compute_type'])
        dialog.enable_trans.setChecked(self.config['enable_translation'])
        dialog.baidu_appid.setText(self.config['baidu_appid'])
        dialog.baidu_key.setText(self.config['baidu_key'])
        dialog.target_lang.setCurrentText(self.config['target_language'])

        if dialog.exec_() == QDialog.Accepted:
            new_config = dialog.get_config()

            # 确保 CPU 设备使用 float32 精度
            if new_config['device'] == 'cpu' and new_config[
                    'compute_type'] != 'float32':
                new_config['compute_type'] = 'float32'

            self.config.update(new_config)
            # 更新全局翻译配置
            global BAIDU_APPID, BAIDU_KEY
            BAIDU_APPID = self.config['baidu_appid']
            BAIDU_KEY = self.config['baidu_key']


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
