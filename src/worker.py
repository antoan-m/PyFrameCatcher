import cv2
import os
from PyQt6.QtCore import QThread, pyqtSignal, QMutex, QWaitCondition, QMutexLocker

class FrameWorker(QThread):
    progress = pyqtSignal(int)
    log = pyqtSignal(str)
    finished = pyqtSignal(dict) # target_alias -> list of ranges

    def __init__(self, video_paths, target_images, matcher):
        super().__init__()
        self.video_paths = video_paths
        self.target_images = target_images # path -> alias
        self.matcher = matcher
        self.mutex = QMutex()
        self.condition = QWaitCondition()
        self._is_running = True
        self._is_paused = False

    def pause(self):
        with QMutexLocker(self.mutex):
            self._is_paused = True
            self.log.emit("Processing paused.")

    def resume(self):
        with QMutexLocker(self.mutex):
            self._is_paused = False
            self.condition.wakeAll()
            self.log.emit("Processing resumed.")

    def stop(self):
        with QMutexLocker(self.mutex):
            self._is_running = False
            self._is_paused = False
            self.condition.wakeAll()
            self.log.emit("Processing stopped by user.")

    def run(self):
        results = {}
        
        # Load target images
        target_data = {}
        for path, alias in self.target_images.items():
            img = cv2.imread(path)
            if img is not None:
                target_data[alias] = img
                results[alias] = []
            else:
                self.log.emit(f"Error: Could not load target image {path}")

        total_videos = len(self.video_paths)
        for v_idx, video_path in enumerate(self.video_paths):
            # Check for stop
            with QMutexLocker(self.mutex):
                if not self._is_running:
                    break

            self.log.emit(f"Processing video: {os.path.basename(video_path)}")
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                self.log.emit(f"Error: Could not open video {video_path}")
                continue

            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            matches_per_target = {alias: [] for alias in target_data}

            frame_idx = 0
            while True:
                # Handle pause and stop
                self.mutex.lock()
                while self._is_paused:
                    self.condition.wait(self.mutex)
                if not self._is_running:
                    self.mutex.unlock()
                    break
                self.mutex.unlock()

                ret, frame = cap.read()
                if not ret:
                    break
                
                timestamp = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
                
                for alias, target_img in target_data.items():
                    if self.matcher.compare(frame, target_img):
                        matches_per_target[alias].append((frame_idx, timestamp))
                        self.log.emit(f"Match found for '{alias}' at {timestamp:.2f}s")
                
                frame_idx += 1
                if frame_idx % 10 == 0: # Update progress every 10 frames
                    p = int(((v_idx + (frame_idx / total_frames)) / total_videos) * 100)
                    self.progress.emit(p)

            cap.release()

            # Group matches into ranges
            for alias, matches in matches_per_target.items():
                ranges = self.matcher.group_matches(matches)
                video_name = os.path.basename(video_path)
                for r in ranges:
                    r['video'] = video_name
                    r['video_path'] = video_path
                results[alias].extend(ranges)
                self.log.emit(f"Found {len(ranges)} occurrences for '{alias}' in {video_name}")

        self.progress.emit(100)
        self.finished.emit(results)
