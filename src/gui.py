from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QListWidget, QPushButton, QLabel, QProgressBar, QTextEdit,
    QFileDialog, QListWidgetItem, QInputDialog, QTableWidget, QTableWidgetItem,
    QHeaderView, QDialog, QComboBox, QFormLayout, QStatusBar, QApplication
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QGuiApplication, QPalette
import os
import csv
import json
import time
from src.worker import FrameWorker
from src.matcher import FrameMatcher
from src.generator import MarkerGenerator

class MarkerWorker(QThread):
    progress = pyqtSignal(int)
    log = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, source_video, results, output_path, mode):
        super().__init__()
        self.source_video = source_video
        self.results = results
        self.output_path = output_path
        self.mode = mode
        self.generator = MarkerGenerator()

    def stop(self):
        self.generator.stop()

    def run(self):
        self.generator.progress.connect(self.progress.emit)
        self.generator.log.connect(self.log.emit)
        self.generator.create_marker_file(self.source_video, self.results, self.output_path, self.mode)
        self.finished.emit()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyFrameCatcher")
        self.resize(1000, 750)

        self.videos = []
        self.images = {} # path -> alias
        self.matcher = FrameMatcher()
        self.worker = None
        self.marker_worker = None
        self.last_results = {}
        self.start_time = 0

        # Progress Animation Setup
        self.shimmer_timer = QTimer()
        self.shimmer_timer.timeout.connect(self.update_shimmer)
        self.shimmer_offset = 0

        # Main Layout
        self.central_widget = QWidget()
        self.central_widget.setObjectName("centralWidget")
        self.setCentralWidget(self.central_widget)
        
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Selection Area
        selection_layout = QHBoxLayout()
        selection_layout.setSpacing(20)
        
        # Video Selection
        video_layout = QVBoxLayout()
        video_label = QLabel("Videos to Process")
        video_label.setStyleSheet("font-weight: bold;")
        video_layout.addWidget(video_label)
        self.video_list = QListWidget()
        video_layout.addWidget(self.video_list)
        self.add_video_btn = QPushButton("Add Videos")
        self.add_video_btn.clicked.connect(self.add_videos)
        video_layout.addWidget(self.add_video_btn)
        selection_layout.addLayout(video_layout)

        # Image Selection
        image_layout = QVBoxLayout()
        image_label = QLabel("Target Images (Double-click to set alias)")
        image_label.setStyleSheet("font-weight: bold;")
        image_layout.addWidget(image_label)
        self.image_list = QListWidget()
        self.image_list.itemDoubleClicked.connect(self.edit_alias)
        image_layout.addWidget(self.image_list)
        self.add_image_btn = QPushButton("Add Images")
        self.add_image_btn.clicked.connect(self.add_images)
        image_layout.addWidget(self.add_image_btn)
        selection_layout.addLayout(image_layout)

        main_layout.addLayout(selection_layout)

        # Controls
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)
        
        self.start_btn = QPushButton("Start Processing")
        self.start_btn.clicked.connect(self.start_processing)
        self.start_btn.setMinimumWidth(150)
        controls_layout.addWidget(self.start_btn)

        self.pause_btn = QPushButton("Pause")
        self.pause_btn.clicked.connect(self.pause_processing)
        self.pause_btn.setEnabled(False)
        controls_layout.addWidget(self.pause_btn)

        self.resume_btn = QPushButton("Resume")
        self.resume_btn.clicked.connect(self.resume_processing)
        self.resume_btn.setEnabled(False)
        controls_layout.addWidget(self.resume_btn)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setObjectName("stop_btn")
        self.stop_btn.clicked.connect(self.stop_processing)
        self.stop_btn.setEnabled(False)
        controls_layout.addWidget(self.stop_btn)

        controls_layout.addStretch()
        main_layout.addLayout(controls_layout)

        # Progress
        progress_info_layout = QHBoxLayout()
        progress_label = QLabel("Total Progress")
        progress_label.setStyleSheet("font-weight: bold;")
        progress_info_layout.addWidget(progress_label)
        
        self.time_label = QLabel("Elapsed: 00:00 | Remaining: --:--")
        progress_info_layout.addStretch()
        progress_info_layout.addWidget(self.time_label)
        main_layout.addLayout(progress_info_layout)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_bar.setFormat("%p%")
        main_layout.addWidget(self.progress_bar)

        self.progress_animation = QPropertyAnimation(self.progress_bar, b"value")
        self.progress_animation.setDuration(300)

        # Results Table
        results_label = QLabel("Results")
        results_label.setStyleSheet("font-weight: bold;")
        main_layout.addWidget(results_label)
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(["Video", "Target Alias", "Time Range (s)", "Frame Range"])
        self.results_table.setSortingEnabled(True)
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        main_layout.addWidget(self.results_table)

        # Export Controls
        export_layout = QHBoxLayout()
        self.export_csv_btn = QPushButton("Export to CSV")
        self.export_csv_btn.setObjectName("csv_btn")
        self.export_csv_btn.clicked.connect(self.export_csv)
        self.export_csv_btn.setEnabled(False)
        export_layout.addWidget(self.export_csv_btn)

        self.export_json_btn = QPushButton("Export to JSON")
        self.export_json_btn.setObjectName("json_btn")
        self.export_json_btn.clicked.connect(self.export_json)
        self.export_json_btn.setEnabled(False)
        export_layout.addWidget(self.export_json_btn)

        self.gen_video_btn = QPushButton("Gen Video Markers")
        self.gen_video_btn.setObjectName("gen_v_btn")
        self.gen_video_btn.clicked.connect(lambda: self.generate_markers("video"))
        self.gen_video_btn.setEnabled(False)
        export_layout.addWidget(self.gen_video_btn)

        self.gen_audio_btn = QPushButton("Gen Audio Markers")
        self.gen_audio_btn.setObjectName("gen_a_btn")
        self.gen_audio_btn.clicked.connect(lambda: self.generate_markers("audio"))
        self.gen_audio_btn.setEnabled(False)
        export_layout.addWidget(self.gen_audio_btn)

        self.gen_both_btn = QPushButton("Gen Both Markers")
        self.gen_both_btn.setObjectName("gen_b_btn")
        self.gen_both_btn.clicked.connect(lambda: self.generate_markers("both"))
        self.gen_both_btn.setEnabled(False)
        export_layout.addWidget(self.gen_both_btn)

        self.cancel_marker_btn = QPushButton("Cancel Generation")
        self.cancel_marker_btn.setObjectName("cancel_marker_btn")
        self.cancel_marker_btn.clicked.connect(self.stop_marker_generation)
        self.cancel_marker_btn.setEnabled(False)
        export_layout.addWidget(self.cancel_marker_btn)

        export_layout.addStretch()
        main_layout.addLayout(export_layout)

        # Explicitly set pointing hand cursor for all buttons
        for btn in self.findChildren(QPushButton):
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

        # Logs
        log_label = QLabel("Logs")
        log_label.setStyleSheet("font-weight: bold;")
        main_layout.addWidget(log_label)
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setStyleSheet("font-family: 'Consolas', 'Monaco', monospace; font-size: 9pt;")
        main_layout.addWidget(self.log_view)

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        self.status_version = QLabel("v0.1.0")
        self.status_version.setStyleSheet("color: #666")
        self.status_author = QLabel("Author: antoan-m")
        self.status_author.setStyleSheet("color: #666")
        self.status_repo = QLabel('<a href="https://github.com/antoan-m/PyFrameCatcher" style="color: #666; text-decoration: none;">GitHub Repo</a>')
        self.status_repo.setOpenExternalLinks(True)
        
        self.status_bar.addPermanentWidget(self.status_version)
        self.status_bar.addPermanentWidget(self.status_author)
        self.status_bar.addPermanentWidget(self.status_repo)

        # Apply Theme
        self.apply_theme()
        
        # Monitor system theme changes if possible
        try:
            QGuiApplication.styleHints().colorSchemeChanged.connect(self.apply_theme)
        except AttributeError:
            pass

    def is_dark_mode(self):
        try:
            # Modern Qt 6.5+ way
            scheme = QGuiApplication.styleHints().colorScheme()
            return scheme == Qt.ColorScheme.Dark
        except AttributeError:
            # Fallback for older PyQt6 versions: Check palette lightness
            palette = QGuiApplication.palette()
            return palette.color(QPalette.ColorGroup.Active, QPalette.ColorRole.Window).lightness() < 128

    def apply_theme(self, *args):
        is_dark = self.is_dark_mode()
        
        if is_dark:
            # Dark Mode Stylesheet
            bg_color = "#1e1e1e"
            card_bg = "#2d2d2d"
            text_color = "#ffffff" # Brighter text
            border_color = "#444"
            input_bg = "#333"
            header_bg = "#3c3c3c"
            progress_bg = "#333"
            accent_blue = "#0098ff" # Lighter blue for dark mode
            hover_blue = "#00b0ff"
        else:
            # Light Mode Stylesheet (Original)
            bg_color = "#f5f5f5"
            card_bg = "white"
            text_color = "#333"
            border_color = "#ddd"
            input_bg = "white"
            header_bg = "#e9ecef"
            progress_bg = "#eee"
            accent_blue = "#007bff"
            hover_blue = "#0056b3"

        self.central_widget.setStyleSheet(f"""
            #centralWidget {{
                background-color: {bg_color};
            }}
            QLabel {{
                font-family: "Segoe UI", "Roboto", sans-serif;
                font-size: 10pt;
                color: {text_color};
            }}
            QPushButton {{
                font-family: "Segoe UI", "Roboto", sans-serif;
                font-size: 10pt;
                background-color: {accent_blue};
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {hover_blue};
            }}
            QPushButton:disabled {{
                background-color: {border_color if is_dark else "#ccc"};
                color: {"#888" if is_dark else "#666"};
            }}
            QPushButton#stop_btn, QPushButton#cancel_marker_btn {{
                background-color: #dc3545;
            }}
            QPushButton#stop_btn:hover, QPushButton#cancel_marker_btn:hover {{
                background-color: #a71d2a;
            }}
            QListWidget, QTableWidget, QTextEdit {{
                font-family: "Segoe UI", "Roboto", sans-serif;
                font-size: 10pt;
                background-color: {input_bg};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 4px;
            }}
            QHeaderView::section {{
                background-color: {header_bg};
                color: {text_color};
                padding: 4px;
                border: 1px solid {border_color};
                font-weight: bold;
            }}
            QProgressBar {{
                font-family: "Segoe UI", "Roboto", sans-serif;
                font-size: 10pt;
                border: 1px solid {border_color};
                border-radius: 5px;
                text-align: center;
                background-color: {progress_bg};
                height: 20px;
                color: {text_color};
            }}
            QProgressBar::chunk {{
                background-color: #05B8CC;
                border-radius: 5px;
            }}
            QStatusBar {{
                background-color: {header_bg};
                color: {text_color};
            }}
        """)
        
        # Reset progress bar to remove hardcoded chunk if it was set during processing
        if not self.worker and not self.marker_worker:
            self.progress_bar.setStyleSheet("")
            self.update_shimmer()

    def update_shimmer(self):
        self.shimmer_offset = (self.shimmer_offset + 2) % 100
        offset = self.shimmer_offset / 100.0
        # Dynamically update style for shimmering effect
        self.progress_bar.setStyleSheet(f"""
            QProgressBar::chunk {{
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #05B8CC, 
                    stop:{max(0, offset-0.15)} #05B8CC, 
                    stop:{offset} #00E5FF, 
                    stop:{min(1, offset+0.15)} #05B8CC, 
                    stop:1 #05B8CC);
                border-radius: 5px;
            }}
        """)

    def format_time(self, seconds):
        if seconds < 0: return "--:--"
        mins, secs = divmod(int(seconds), 60)
        return f"{mins:02d}:{secs:02d}"

    def update_time_stats(self, progress_value):
        if self.start_time == 0: return
        
        elapsed = time.time() - self.start_time
        if progress_value > 0:
            total_est = elapsed / (progress_value / 100.0)
            remaining = total_est - elapsed
            self.time_label.setText(f"Elapsed: {self.format_time(elapsed)} | Remaining: {self.format_time(remaining)}")
        else:
            self.time_label.setText(f"Elapsed: {self.format_time(elapsed)} | Remaining: --:--")

    def clean_path(self, path):
        """Clean and normalize the file path."""
        if path.startswith("file://"):
            path = path[7:]
        # On some systems, file:// might have 3 slashes if it's absolute
        if path.startswith("//") and os.name == 'posix':
            path = "/" + path.lstrip("/")
        return os.path.abspath(path)

    def add_videos(self):
        try:
            files, filter_used = QFileDialog.getOpenFileNames(
                self, "Select Videos", "", "Videos (*.mp4 *.avi *.mkv *.mov);;All Files (*)"
            )
            for raw_file in files:
                file = self.clean_path(raw_file)
                if not os.path.exists(file):
                    self.add_log(f"WARNING: File does not exist: {file}")
                    continue
                if file not in self.videos:
                    self.videos.append(file)
                    self.video_list.addItem(os.path.basename(file))
        except Exception as e:
            self.add_log(f"ERROR adding videos: {str(e)}")

    def add_images(self):
        try:
            files, filter_used = QFileDialog.getOpenFileNames(
                self, "Select Images", "", "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*)"
            )
            for raw_file in files:
                file = self.clean_path(raw_file)
                if not os.path.exists(file):
                    self.add_log(f"WARNING: File does not exist: {file}")
                    continue
                if file not in self.images:
                    alias = os.path.basename(file)
                    self.images[file] = alias
                    item = QListWidgetItem(f"{alias} ({file})")
                    item.setData(Qt.ItemDataRole.UserRole, file)
                    self.image_list.addItem(item)
        except Exception as e:
            self.add_log(f"ERROR adding images: {str(e)}")

    def edit_alias(self, item):
        file = item.data(Qt.ItemDataRole.UserRole)
        old_alias = self.images[file]
        new_alias, ok = QInputDialog.getText(self, "Edit Alias", "Alias:", text=old_alias)
        if ok and new_alias:
            self.images[file] = new_alias
            item.setText(f"{new_alias} ({file})")

    def start_processing(self):
        if not self.videos or not self.images:
            self.add_log("Error: Please add at least one video and one target image.")
            return

        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.resume_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.add_video_btn.setEnabled(False)
        self.add_image_btn.setEnabled(False)
        self.export_csv_btn.setEnabled(False)
        self.export_json_btn.setEnabled(False)
        self.gen_video_btn.setEnabled(False)
        self.gen_audio_btn.setEnabled(False)
        self.gen_both_btn.setEnabled(False)
        
        self.progress_bar.setValue(0)
        self.start_time = time.time()
        self.add_log("Starting processing...")
        self.status_bar.showMessage("Processing videos...")
        self.shimmer_timer.start(50) # 20 FPS shimmer

        self.worker = FrameWorker(self.videos, self.images, self.matcher)
        self.worker.progress.connect(self.update_progress)
        self.worker.log.connect(self.add_log)
        self.worker.finished.connect(self.processing_finished)
        self.worker.start()

    def pause_processing(self):
        if self.worker:
            self.worker.pause()
            self.pause_btn.setEnabled(False)
            self.resume_btn.setEnabled(True)
            self.shimmer_timer.stop()
            self.status_bar.showMessage("Processing paused.")

    def resume_processing(self):
        if self.worker:
            self.worker.resume()
            self.pause_btn.setEnabled(True)
            self.resume_btn.setEnabled(False)
            self.shimmer_timer.start(50)
            self.status_bar.showMessage("Processing videos...")

    def stop_processing(self):
        if self.worker:
            self.worker.stop()
            self.stop_btn.setEnabled(False)
            self.pause_btn.setEnabled(False)
            self.resume_btn.setEnabled(False)
            self.shimmer_timer.stop()
            self.status_bar.showMessage("Processing stopped.")

    def update_progress(self, value):
        self.progress_animation.stop()
        self.progress_animation.setEndValue(value)
        self.progress_animation.start()
        self.update_time_stats(value)

    def add_log(self, message):
        self.log_view.append(message)

    def processing_finished(self, results):
        self.add_log("Processing finished.")
        self.status_bar.showMessage("Processing finished.")
        QApplication.beep()
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.resume_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.add_video_btn.setEnabled(True)
        self.add_image_btn.setEnabled(True)
        self.shimmer_timer.stop()
        self.apply_theme() # Refresh theme and reset progress bar style
        
        self.last_results = results
        if any(results.values()):
            self.export_csv_btn.setEnabled(True)
            self.export_json_btn.setEnabled(True)
            self.gen_video_btn.setEnabled(True)
            self.gen_audio_btn.setEnabled(True)
            self.gen_both_btn.setEnabled(True)
        self.display_results(results)

    def generate_markers(self, mode):
        if not self.last_results:
            return

        source_video = None
        for alias, ranges in self.last_results.items():
            if ranges:
                source_video = ranges[0].get('video_path')
                break
        
        if not source_video:
            if self.videos:
                source_video = self.videos[0]
            else:
                self.add_log("Error: No source video found for marker generation.")
                return

        # Prepare output path
        ext = ".mp4" if mode != "audio" else ".wav"
        default_name = os.path.splitext(os.path.basename(source_video))[0] + "_markers" + ext
        path, _ = QFileDialog.getSaveFileName(self, f"Save {mode.capitalize()} Marker File", default_name, f"Files (*{ext})")
        
        if path:
            self.start_btn.setEnabled(False)
            self.gen_video_btn.setEnabled(False)
            self.gen_audio_btn.setEnabled(False)
            self.gen_both_btn.setEnabled(False)
            self.export_csv_btn.setEnabled(False)
            self.export_json_btn.setEnabled(False)
            self.cancel_marker_btn.setEnabled(True)
            
            self.progress_bar.setValue(0)
            self.start_time = time.time()
            self.status_bar.showMessage(f"Generating {mode} markers...")

            # Flatten results for the generator
            flat_results = []
            for alias, ranges in self.last_results.items():
                target_path = None
                for p, a in self.images.items():
                    if a == alias:
                        target_path = p
                        break
                
                for r in ranges:
                    if r.get('video_path') == source_video or not r.get('video_path'):
                        flat_results.append({
                            "start_frame": r['start_frame'],
                            "end_frame": r['end_frame'],
                            "target_path": target_path
                        })

            self.marker_worker = MarkerWorker(source_video, flat_results, path, mode)
            self.marker_worker.progress.connect(self.update_progress)
            self.marker_worker.log.connect(self.add_log)
            self.marker_worker.finished.connect(self.marker_generation_finished)
            self.marker_worker.start()

    def stop_marker_generation(self):
        if self.marker_worker:
            self.marker_worker.stop()
            self.cancel_marker_btn.setEnabled(False)
            self.add_log("Marker generation cancellation requested...")
            self.status_bar.showMessage("Cancelling marker generation...")

    def marker_generation_finished(self):
        self.add_log("Marker generation process ended.")
        self.status_bar.showMessage("Marker generation ended.")
        QApplication.beep()
        self.start_btn.setEnabled(True)
        self.gen_video_btn.setEnabled(True)
        self.gen_audio_btn.setEnabled(True)
        self.gen_both_btn.setEnabled(True)
        self.export_csv_btn.setEnabled(True)
        self.export_json_btn.setEnabled(True)
        self.cancel_marker_btn.setEnabled(False)
        self.progress_bar.setValue(100)
        self.apply_theme() # Refresh theme and reset progress bar style

    def display_results(self, results):
        self.results_table.setRowCount(0)
        self.results_table.setSortingEnabled(False)
        row = 0
        for alias, ranges in results.items():
            for r in ranges:
                self.results_table.insertRow(row)
                
                video_item = QTableWidgetItem(r.get('video', 'Unknown'))
                alias_item = QTableWidgetItem(alias)
                time_item = QTableWidgetItem(f"{r['start_time']:.2f} - {r['end_time']:.2f}")
                frame_item = QTableWidgetItem(f"{r['start_frame']} - {r['end_frame']}")
                
                self.results_table.setItem(row, 0, video_item)
                self.results_table.setItem(row, 1, alias_item)
                self.results_table.setItem(row, 2, time_item)
                self.results_table.setItem(row, 3, frame_item)
                
                row += 1
        self.results_table.setSortingEnabled(True)

    def export_csv(self):
        if not self.last_results:
            return
        
        path, _ = QFileDialog.getSaveFileName(self, "Export Results as CSV", "", "CSV Files (*.csv)")
        if path:
            try:
                with open(path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Video", "Target Alias", "Start Time (s)", "End Time (s)", "Start Frame", "End Frame"])
                    for alias, ranges in self.last_results.items():
                        for r in ranges:
                            writer.writerow([
                                r.get('video', 'Unknown'),
                                alias,
                                f"{r['start_time']:.2f}",
                                f"{r['end_time']:.2f}",
                                r['start_frame'],
                                r['end_frame']
                            ])
                self.add_log(f"Results exported to {path}")
            except Exception as e:
                self.add_log(f"Error exporting CSV: {str(e)}")

    def export_json(self):
        if not self.last_results:
            return
        
        path, _ = QFileDialog.getSaveFileName(self, "Export Results as JSON", "", "JSON Files (*.json)")
        if path:
            try:
                with open(path, 'w') as f:
                    json.dump(self.last_results, f, indent=4)
                self.add_log(f"Results exported to {path}")
            except Exception as e:
                self.add_log(f"Error exporting JSON: {str(e)}")

    def update_shimmer(self):
        self.shimmer_offset = (self.shimmer_offset + 2) % 100
        offset = self.shimmer_offset / 100.0
        # Dynamically update style for shimmering effect
        self.progress_bar.setStyleSheet(f"""
            QProgressBar::chunk {{
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #05B8CC, 
                    stop:{max(0, offset-0.15)} #05B8CC, 
                    stop:{offset} #00E5FF, 
                    stop:{min(1, offset+0.15)} #05B8CC, 
                    stop:1 #05B8CC);
                border-radius: 5px;
            }}
        """)

    def format_time(self, seconds):
        if seconds < 0: return "--:--"
        mins, secs = divmod(int(seconds), 60)
        return f"{mins:02d}:{secs:02d}"

    def update_time_stats(self, progress_value):
        if self.start_time == 0: return
        
        elapsed = time.time() - self.start_time
        if progress_value > 0:
            total_est = elapsed / (progress_value / 100.0)
            remaining = total_est - elapsed
            self.time_label.setText(f"Elapsed: {self.format_time(elapsed)} | Remaining: {self.format_time(remaining)}")
        else:
            self.time_label.setText(f"Elapsed: {self.format_time(elapsed)} | Remaining: --:--")

    def clean_path(self, path):
        """Clean and normalize the file path."""
        if path.startswith("file://"):
            path = path[7:]
        # On some systems, file:// might have 3 slashes if it's absolute
        if path.startswith("//") and os.name == 'posix':
            path = "/" + path.lstrip("/")
        return os.path.abspath(path)

    def add_videos(self):
        try:
            files, filter_used = QFileDialog.getOpenFileNames(
                self, "Select Videos", "", "Videos (*.mp4 *.avi *.mkv *.mov);;All Files (*)"
            )
            for raw_file in files:
                file = self.clean_path(raw_file)
                if not os.path.exists(file):
                    self.add_log(f"WARNING: File does not exist: {file}")
                    continue
                if file not in self.videos:
                    self.videos.append(file)
                    self.video_list.addItem(os.path.basename(file))
        except Exception as e:
            self.add_log(f"ERROR adding videos: {str(e)}")

    def add_images(self):
        try:
            files, filter_used = QFileDialog.getOpenFileNames(
                self, "Select Images", "", "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*)"
            )
            for raw_file in files:
                file = self.clean_path(raw_file)
                if not os.path.exists(file):
                    self.add_log(f"WARNING: File does not exist: {file}")
                    continue
                if file not in self.images:
                    alias = os.path.basename(file)
                    self.images[file] = alias
                    item = QListWidgetItem(f"{alias} ({file})")
                    item.setData(Qt.ItemDataRole.UserRole, file)
                    self.image_list.addItem(item)
        except Exception as e:
            self.add_log(f"ERROR adding images: {str(e)}")

    def edit_alias(self, item):
        file = item.data(Qt.ItemDataRole.UserRole)
        old_alias = self.images[file]
        new_alias, ok = QInputDialog.getText(self, "Edit Alias", "Alias:", text=old_alias)
        if ok and new_alias:
            self.images[file] = new_alias
            item.setText(f"{new_alias} ({file})")

    def start_processing(self):
        if not self.videos or not self.images:
            self.add_log("Error: Please add at least one video and one target image.")
            return

        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.resume_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.add_video_btn.setEnabled(False)
        self.add_image_btn.setEnabled(False)
        self.export_csv_btn.setEnabled(False)
        self.export_json_btn.setEnabled(False)
        self.gen_video_btn.setEnabled(False)
        self.gen_audio_btn.setEnabled(False)
        self.gen_both_btn.setEnabled(False)
        
        self.progress_bar.setValue(0)
        self.start_time = time.time()
        self.add_log("Starting processing...")
        self.status_bar.showMessage("Processing videos...")
        self.shimmer_timer.start(50) # 20 FPS shimmer

        self.worker = FrameWorker(self.videos, self.images, self.matcher)
        self.worker.progress.connect(self.update_progress)
        self.worker.log.connect(self.add_log)
        self.worker.finished.connect(self.processing_finished)
        self.worker.start()

    def pause_processing(self):
        if self.worker:
            self.worker.pause()
            self.pause_btn.setEnabled(False)
            self.resume_btn.setEnabled(True)
            self.shimmer_timer.stop()
            self.status_bar.showMessage("Processing paused.")

    def resume_processing(self):
        if self.worker:
            self.worker.resume()
            self.pause_btn.setEnabled(True)
            self.resume_btn.setEnabled(False)
            self.shimmer_timer.start(50)
            self.status_bar.showMessage("Processing videos...")

    def stop_processing(self):
        if self.worker:
            self.worker.stop()
            self.stop_btn.setEnabled(False)
            self.pause_btn.setEnabled(False)
            self.resume_btn.setEnabled(False)
            self.shimmer_timer.stop()
            self.status_bar.showMessage("Processing stopped.")

    def update_progress(self, value):
        self.progress_animation.stop()
        self.progress_animation.setEndValue(value)
        self.progress_animation.start()
        self.update_time_stats(value)

    def add_log(self, message):
        self.log_view.append(message)

    def processing_finished(self, results):
        self.add_log("Processing finished.")
        self.status_bar.showMessage("Processing finished.")
        QApplication.beep()
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.resume_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.add_video_btn.setEnabled(True)
        self.add_image_btn.setEnabled(True)
        self.shimmer_timer.stop()
        self.progress_bar.setStyleSheet("") # Reset to standard chunk
        
        self.last_results = results
        if any(results.values()):
            self.export_csv_btn.setEnabled(True)
            self.export_json_btn.setEnabled(True)
            self.gen_video_btn.setEnabled(True)
            self.gen_audio_btn.setEnabled(True)
            self.gen_both_btn.setEnabled(True)
        self.display_results(results)

    def generate_markers(self, mode):
        if not self.last_results:
            return

        source_video = None
        for alias, ranges in self.last_results.items():
            if ranges:
                source_video = ranges[0].get('video_path')
                break
        
        if not source_video:
            if self.videos:
                source_video = self.videos[0]
            else:
                self.add_log("Error: No source video found for marker generation.")
                return

        # Prepare output path
        ext = ".mp4" if mode != "audio" else ".wav"
        default_name = os.path.splitext(os.path.basename(source_video))[0] + "_markers" + ext
        path, _ = QFileDialog.getSaveFileName(self, f"Save {mode.capitalize()} Marker File", default_name, f"Files (*{ext})")
        
        if path:
            self.start_btn.setEnabled(False)
            self.gen_video_btn.setEnabled(False)
            self.gen_audio_btn.setEnabled(False)
            self.gen_both_btn.setEnabled(False)
            self.export_csv_btn.setEnabled(False)
            self.export_json_btn.setEnabled(False)
            self.cancel_marker_btn.setEnabled(True)
            
            self.progress_bar.setValue(0)
            self.start_time = time.time()
            self.status_bar.showMessage(f"Generating {mode} markers...")

            # Flatten results for the generator
            flat_results = []
            for alias, ranges in self.last_results.items():
                target_path = None
                for p, a in self.images.items():
                    if a == alias:
                        target_path = p
                        break
                
                for r in ranges:
                    if r.get('video_path') == source_video or not r.get('video_path'):
                        flat_results.append({
                            "start_frame": r['start_frame'],
                            "end_frame": r['end_frame'],
                            "target_path": target_path
                        })

            self.marker_worker = MarkerWorker(source_video, flat_results, path, mode)
            self.marker_worker.progress.connect(self.update_progress)
            self.marker_worker.log.connect(self.add_log)
            self.marker_worker.finished.connect(self.marker_generation_finished)
            self.marker_worker.start()

    def stop_marker_generation(self):
        if self.marker_worker:
            self.marker_worker.stop()
            self.cancel_marker_btn.setEnabled(False)
            self.add_log("Marker generation cancellation requested...")
            self.status_bar.showMessage("Cancelling marker generation...")

    def marker_generation_finished(self):
        self.add_log("Marker generation process ended.")
        self.status_bar.showMessage("Marker generation ended.")
        QApplication.beep()
        self.start_btn.setEnabled(True)
        self.gen_video_btn.setEnabled(True)
        self.gen_audio_btn.setEnabled(True)
        self.gen_both_btn.setEnabled(True)
        self.export_csv_btn.setEnabled(True)
        self.export_json_btn.setEnabled(True)
        self.cancel_marker_btn.setEnabled(False)
        self.progress_bar.setValue(100)

    def display_results(self, results):
        self.results_table.setRowCount(0)
        self.results_table.setSortingEnabled(False)
        row = 0
        for alias, ranges in results.items():
            for r in ranges:
                self.results_table.insertRow(row)
                
                video_item = QTableWidgetItem(r.get('video', 'Unknown'))
                alias_item = QTableWidgetItem(alias)
                time_item = QTableWidgetItem(f"{r['start_time']:.2f} - {r['end_time']:.2f}")
                frame_item = QTableWidgetItem(f"{r['start_frame']} - {r['end_frame']}")
                
                self.results_table.setItem(row, 0, video_item)
                self.results_table.setItem(row, 1, alias_item)
                self.results_table.setItem(row, 2, time_item)
                self.results_table.setItem(row, 3, frame_item)
                
                row += 1
        self.results_table.setSortingEnabled(True)

    def export_csv(self):
        if not self.last_results:
            return
        
        path, _ = QFileDialog.getSaveFileName(self, "Export Results as CSV", "", "CSV Files (*.csv)")
        if path:
            try:
                with open(path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Video", "Target Alias", "Start Time (s)", "End Time (s)", "Start Frame", "End Frame"])
                    for alias, ranges in self.last_results.items():
                        for r in ranges:
                            writer.writerow([
                                r.get('video', 'Unknown'),
                                alias,
                                f"{r['start_time']:.2f}",
                                f"{r['end_time']:.2f}",
                                r['start_frame'],
                                r['end_frame']
                            ])
                self.add_log(f"Results exported to {path}")
            except Exception as e:
                self.add_log(f"Error exporting CSV: {str(e)}")

    def export_json(self):
        if not self.last_results:
            return
        
        path, _ = QFileDialog.getSaveFileName(self, "Export Results as JSON", "", "JSON Files (*.json)")
        if path:
            try:
                with open(path, 'w') as f:
                    json.dump(self.last_results, f, indent=4)
                self.add_log(f"Results exported to {path}")
            except Exception as e:
                self.add_log(f"Error exporting JSON: {str(e)}")
