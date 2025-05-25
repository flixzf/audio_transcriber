#!/usr/bin/env python3
"""
음성파일 전사 프로그램 (GUI 버전)
- Whisper + pyannote-audio를 사용한 전사 및 화자 분리
- GUI 인터페이스로 쉬운 사용
- txt, csv, json 형식으로 결과 저장
"""

import sys
import os
import csv
import json
import tempfile
import subprocess
import threading
from datetime import timedelta
from pathlib import Path

from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QPushButton, QLabel, QFileDialog, QComboBox,
                             QProgressBar, QTextEdit, QGroupBox, QGridLayout,
                             QCheckBox, QSpinBox, QMessageBox, QTabWidget)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QIcon

import whisper
from pyannote.audio import Pipeline
import torch

class TranscriptionWorker(QThread):
    """백그라운드에서 전사 작업을 수행하는 워커 스레드"""
    progress_updated = Signal(int, str)
    finished = Signal(str, list)
    error_occurred = Signal(str)

    def __init__(self, audio_file, model_size, device, hf_token, use_diarization):
        super().__init__()
        self.audio_file = audio_file
        self.model_size = model_size
        self.device = device
        self.hf_token = hf_token
        self.use_diarization = use_diarization

    def run(self):
        try:
            # Whisper 모델 로드
            self.progress_updated.emit(10, "Whisper 모델 로딩 중...")
            model = whisper.load_model(self.model_size, device=self.device)
            
            # 음성 전사
            self.progress_updated.emit(30, "음성 전사 진행 중...")
            result = model.transcribe(self.audio_file, fp16=False, verbose=True)
            whisper_segments = result["segments"]
            
            merged_segments = []
            
            if self.use_diarization and self.hf_token:
                # 화자 분리
                self.progress_updated.emit(60, "화자 분리 진행 중...")
                diar_segments = self.diarize_audio(self.audio_file, self.hf_token)
                
                # 전사와 화자 분리 결과 병합
                self.progress_updated.emit(80, "결과 병합 중...")
                merged_segments = self.merge_transcription_and_diarization(whisper_segments, diar_segments)
            else:
                # 화자 분리 없이 전사만
                for seg in whisper_segments:
                    merged_segments.append({
                        "speaker": "Speaker_1",
                        "start": seg["start"],
                        "end": seg["end"],
                        "text": seg["text"].strip()
                    })
            
            self.progress_updated.emit(100, "완료!")
            self.finished.emit("성공적으로 전사되었습니다!", merged_segments)
            
        except Exception as e:
            self.error_occurred.emit(f"오류 발생: {str(e)}")

    def diarize_audio(self, file_path, hf_token):
        """화자 분리 수행"""
        try:
            pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=hf_token
            )
            diarization = pipeline(file_path)
            segments = []
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                segments.append({
                    "start": turn.start, 
                    "end": turn.end,
                    "speaker": speaker
                })
            return segments
        except Exception as e:
            print(f"화자 분리 오류: {e}")
            return []

    def merge_transcription_and_diarization(self, whisper_segments, diar_segments):
        """전사 결과와 화자 분리 결과를 병합"""
        merged = []
        for seg in whisper_segments:
            # 가장 많이 겹치는 화자 찾기
            speaker = "Speaker_Unknown"
            overlaps = [d for d in diar_segments
                       if not (d["end"] < seg["start"] or d["start"] > seg["end"])]
            if overlaps:
                best_overlap = max(overlaps, 
                                 key=lambda d: min(d["end"], seg["end"]) - max(d["start"], seg["start"]))
                speaker = best_overlap["speaker"]
            
            merged.append({
                "speaker": speaker,
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"].strip()
            })
        return merged

class AudioTranscriberGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.segments = []
        self.audio_file = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("음성파일 전사 프로그램 v1.0")
        self.setGeometry(100, 100, 800, 600)
        
        # 메인 위젯
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # 제목
        title = QLabel("🎵 음성파일 전사 프로그램")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 탭 위젯
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # 메인 탭
        main_tab = QWidget()
        tab_widget.addTab(main_tab, "전사하기")
        self.setup_main_tab(main_tab)
        
        # 설정 탭
        settings_tab = QWidget()
        tab_widget.addTab(settings_tab, "설정")
        self.setup_settings_tab(settings_tab)
        
        # 상태바
        self.statusBar().showMessage("준비됨")

    def setup_main_tab(self, parent):
        layout = QVBoxLayout(parent)
        
        # 파일 선택 그룹
        file_group = QGroupBox("📁 파일 선택")
        file_layout = QHBoxLayout(file_group)
        
        self.file_label = QLabel("파일을 선택하세요...")
        self.file_label.setStyleSheet("QLabel { background-color: #f0f0f0; padding: 8px; border: 1px solid #ccc; }")
        file_layout.addWidget(self.file_label)
        
        self.browse_btn = QPushButton("파일 선택")
        self.browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(self.browse_btn)
        
        layout.addWidget(file_group)
        
        # 옵션 그룹
        options_group = QGroupBox("⚙️ 전사 옵션")
        options_layout = QGridLayout(options_group)
        
        # 모델 크기
        options_layout.addWidget(QLabel("Whisper 모델:"), 0, 0)
        self.model_combo = QComboBox()
        self.model_combo.addItems(["tiny", "base", "small", "medium", "large"])
        self.model_combo.setCurrentText("medium")
        options_layout.addWidget(self.model_combo, 0, 1)
        
        # 디바이스
        options_layout.addWidget(QLabel("처리 장치:"), 0, 2)
        self.device_combo = QComboBox()
        if torch.cuda.is_available():
            self.device_combo.addItems(["cpu", "cuda"])
            self.device_combo.setCurrentText("cuda")
        else:
            self.device_combo.addItems(["cpu"])
        options_layout.addWidget(self.device_combo, 0, 3)
        
        # 화자 분리 옵션
        self.diarization_check = QCheckBox("화자 분리 사용")
        self.diarization_check.setChecked(True)
        options_layout.addWidget(self.diarization_check, 1, 0)
        
        # HuggingFace 토큰
        options_layout.addWidget(QLabel("HF 토큰:"), 1, 1)
        self.hf_token_combo = QComboBox()
        self.hf_token_combo.setEditable(True)
        self.hf_token_combo.setPlaceholderText("HuggingFace 토큰 입력")
        options_layout.addWidget(self.hf_token_combo, 1, 2, 1, 2)
        
        layout.addWidget(options_group)
        
        # 실행 버튼
        self.start_btn = QPushButton("🚀 전사 시작")
        self.start_btn.clicked.connect(self.start_transcription)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        layout.addWidget(self.start_btn)
        
        # 진행률 표시
        progress_group = QGroupBox("📊 진행 상황")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("대기 중...")
        progress_layout.addWidget(self.status_label)
        
        layout.addWidget(progress_group)
        
        # 결과 표시
        result_group = QGroupBox("📝 전사 결과")
        result_layout = QVBoxLayout(result_group)
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setMaximumHeight(200)
        result_layout.addWidget(self.result_text)
        
        # 저장 버튼들
        save_layout = QHBoxLayout()
        
        self.save_txt_btn = QPushButton("💾 TXT 저장")
        self.save_txt_btn.clicked.connect(lambda: self.save_results("txt"))
        self.save_txt_btn.setEnabled(False)
        save_layout.addWidget(self.save_txt_btn)
        
        self.save_csv_btn = QPushButton("📊 CSV 저장")
        self.save_csv_btn.clicked.connect(lambda: self.save_results("csv"))
        self.save_csv_btn.setEnabled(False)
        save_layout.addWidget(self.save_csv_btn)
        
        self.save_json_btn = QPushButton("🔧 JSON 저장")
        self.save_json_btn.clicked.connect(lambda: self.save_results("json"))
        self.save_json_btn.setEnabled(False)
        save_layout.addWidget(self.save_json_btn)
        
        self.open_folder_btn = QPushButton("📂 폴더 열기")
        self.open_folder_btn.clicked.connect(self.open_output_folder)
        self.open_folder_btn.setEnabled(False)
        save_layout.addWidget(self.open_folder_btn)
        
        result_layout.addLayout(save_layout)
        layout.addWidget(result_group)

    def setup_settings_tab(self, parent):
        layout = QVBoxLayout(parent)
        
        settings_group = QGroupBox("🔧 고급 설정")
        settings_layout = QGridLayout(settings_group)
        
        # 출력 폴더
        settings_layout.addWidget(QLabel("출력 폴더:"), 0, 0)
        self.output_folder = QLabel(str(Path.cwd()))
        self.output_folder.setStyleSheet("QLabel { background-color: #f0f0f0; padding: 8px; border: 1px solid #ccc; }")
        settings_layout.addWidget(self.output_folder, 0, 1)
        
        output_browse_btn = QPushButton("변경")
        output_browse_btn.clicked.connect(self.browse_output_folder)
        settings_layout.addWidget(output_browse_btn, 0, 2)
        
        layout.addWidget(settings_group)
        
        # 정보 그룹
        info_group = QGroupBox("ℹ️ 프로그램 정보")
        info_layout = QVBoxLayout(info_group)
        
        info_text = """
        <h3>음성파일 전사 프로그램 v1.0</h3>
        <p><b>사용 기술:</b></p>
        <ul>
        <li>OpenAI Whisper: 음성-텍스트 변환</li>
        <li>pyannote-audio: 화자 분리</li>
        <li>PyQt5: 사용자 인터페이스</li>
        </ul>
        
        <p><b>지원 형식:</b> MP3, WAV, FLAC, M4A, OGG 등</p>
        <p><b>출력 형식:</b> TXT, CSV, JSON</p>
        
        <p><b>사용법:</b></p>
        <ol>
        <li>음성 파일을 선택하세요</li>
        <li>원하는 옵션을 설정하세요</li>
        <li>HuggingFace 토큰을 입력하세요 (화자 분리용)</li>
        <li>'전사 시작' 버튼을 클릭하세요</li>
        </ol>
        
        <p><b>주의사항:</b></p>
        <ul>
        <li>화자 분리를 사용하려면 HuggingFace 토큰이 필요합니다</li>
        <li>GPU가 있으면 'cuda'를 선택하여 더 빠른 처리가 가능합니다</li>
        <li>긴 파일일수록 처리 시간이 더 오래 걸립니다</li>
        </ul>
        """
        
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        info_layout.addWidget(info_label)
        
        layout.addWidget(info_group)
        layout.addStretch()

    def browse_file(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, 
            "음성 파일 선택", 
            "", 
            "Audio Files (*.mp3 *.wav *.flac *.m4a *.ogg *.aac);;All Files (*)"
        )
        
        if file_path:
            self.audio_file = file_path
            self.file_label.setText(Path(file_path).name)
            self.statusBar().showMessage(f"파일 선택됨: {Path(file_path).name}")

    def browse_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "출력 폴더 선택")
        if folder:
            self.output_folder.setText(folder)

    def start_transcription(self):
        if not self.audio_file:
            QMessageBox.warning(self, "경고", "먼저 음성 파일을 선택해주세요.")
            return
        
        hf_token = self.hf_token_combo.currentText().strip()
        use_diarization = self.diarization_check.isChecked()
        
        if use_diarization and not hf_token:
            QMessageBox.warning(self, "경고", "화자 분리를 사용하려면 HuggingFace 토큰을 입력해주세요.")
            return
        
        # UI 상태 변경
        self.start_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("전사 준비 중...")
        self.result_text.clear()
        
        # 토큰 히스토리에 추가
        if hf_token and hf_token not in [self.hf_token_combo.itemText(i) for i in range(self.hf_token_combo.count())]:
            self.hf_token_combo.addItem(hf_token)
        
        # 워커 스레드 시작
        self.worker = TranscriptionWorker(
            self.audio_file,
            self.model_combo.currentText(),
            self.device_combo.currentText(),
            hf_token if use_diarization else None,
            use_diarization
        )
        
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.finished.connect(self.transcription_finished)
        self.worker.error_occurred.connect(self.transcription_error)
        
        self.worker.start()

    def update_progress(self, value, message):
        self.progress_bar.setValue(value)
        self.status_label.setText(message)
        self.statusBar().showMessage(message)

    def transcription_finished(self, message, segments):
        self.segments = segments
        
        # 결과 텍스트 표시
        result_text = ""
        for seg in segments:
            result_text += f"[{seg['speaker']}] {seg['text']}\n"
        
        self.result_text.setText(result_text)
        
        # UI 상태 복원
        self.start_btn.setEnabled(True)
        self.save_txt_btn.setEnabled(True)
        self.save_csv_btn.setEnabled(True)
        self.save_json_btn.setEnabled(True)
        self.open_folder_btn.setEnabled(True)
        
        self.statusBar().showMessage("전사 완료!")
        QMessageBox.information(self, "완료", message)

    def transcription_error(self, error_message):
        self.start_btn.setEnabled(True)
        self.statusBar().showMessage("오류 발생")
        QMessageBox.critical(self, "오류", error_message)

    def save_results(self, format_type):
        if not self.segments:
            QMessageBox.warning(self, "경고", "저장할 결과가 없습니다.")
            return
        
        basename = Path(self.audio_file).stem
        output_dir = Path(self.output_folder.text())
        
        try:
            if format_type == "txt":
                file_path = output_dir / f"transcript_{basename}.txt"
                with open(file_path, "w", encoding="utf-8") as f:
                    for seg in self.segments:
                        f.write(f"[{seg['speaker']}] {seg['text']}\n")
            
            elif format_type == "csv":
                file_path = output_dir / f"transcript_{basename}.csv"
                with open(file_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["start_time", "end_time", "speaker", "text"])
                    for seg in self.segments:
                        writer.writerow([
                            str(timedelta(seconds=int(seg["start"]))),
                            str(timedelta(seconds=int(seg["end"]))),
                            seg["speaker"],
                            seg["text"]
                        ])
            
            elif format_type == "json":
                file_path = output_dir / f"transcript_{basename}.json"
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(self.segments, f, ensure_ascii=False, indent=2)
            
            QMessageBox.information(self, "저장 완료", f"파일이 저장되었습니다:\n{file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "저장 오류", f"파일 저장 중 오류가 발생했습니다:\n{str(e)}")

    def open_output_folder(self):
        output_dir = self.output_folder.text()
        try:
            if sys.platform == "win32":
                os.startfile(output_dir)
            elif sys.platform == "darwin":
                subprocess.run(["open", output_dir])
            else:
                subprocess.run(["xdg-open", output_dir])
        except Exception as e:
            QMessageBox.warning(self, "오류", f"폴더를 열 수 없습니다:\n{str(e)}")

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("음성파일 전사 프로그램")
    
    # 한글 폰트 설정
    font = QFont("Malgun Gothic", 9)
    app.setFont(font)
    
    window = AudioTranscriberGUI()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 