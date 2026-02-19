import cv2
import numpy as np
import os
import subprocess
import time
from PyQt6.QtCore import QObject, pyqtSignal

class MarkerGenerator(QObject):
    progress = pyqtSignal(int)
    log = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.stop_requested = False

    def stop(self):
        self.stop_requested = True

    def get_video_properties(self, video_path):
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
        
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        cap.release()
        return {
            "width": width,
            "height": height,
            "fps": fps,
            "total_frames": total_frames
        }

    def create_marker_file(self, source_video, results, output_path, mode="both"):
        """
        results: list of dicts with start_frame, end_frame, target_path
        mode: "video", "audio", or "both"
        """
        self.stop_requested = False
        props = self.get_video_properties(source_video)
        width, height = props["width"], props["height"]
        fps = props["fps"]
        total_frames = props["total_frames"]

        temp_video = "temp_marker_video.mp4"
        temp_audio = "temp_marker_audio.wav"

        # 1. Generate Video if needed
        if mode in ["video", "both"]:
            self.log.emit("Generating marker video frames...")
            # Use 'mp4v' or 'avc1'
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))

            # Pre-load and resize images
            target_images = {}
            for r in results:
                if self.stop_requested: break
                t_path = r["target_path"]
                if t_path not in target_images:
                    img = cv2.imread(t_path)
                    if img is not None:
                        # Resize/letterbox to fit video
                        target_images[t_path] = self._resize_to_fit(img, width, height)

            # Map frames to images for fast lookup
            frame_map = {}
            for r in results:
                if self.stop_requested: break
                for f in range(r["start_frame"], r["end_frame"] + 1):
                    frame_map[f] = r["target_path"]

            black_frame = np.zeros((height, width, 3), np.uint8)
            for f in range(total_frames):
                if self.stop_requested: break
                if f in frame_map:
                    img_path = frame_map[f]
                    if img_path in target_images:
                        out.write(target_images[img_path])
                    else:
                        out.write(black_frame)
                else:
                    out.write(black_frame)
                
                if f % 100 == 0:
                    self.progress.emit(int((f / total_frames) * 50)) # First 50% for video

            out.release()
            if self.stop_requested:
                if os.path.exists(temp_video): os.remove(temp_video)
                return
            self.log.emit("Marker video frames generated.")

        if self.stop_requested: return

        # 2. Generate Audio if needed
        if mode in ["audio", "both"]:
            self.log.emit("Generating audio tones...")
            duration = total_frames / fps
            
            tone_cmd = ["ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=stereo:d={duration}"]
            
            filter_str = ""
            inputs = ["[0:a]"]
            for i, r in enumerate(results):
                if self.stop_requested: break
                s_t_ms = int((r["start_frame"] / fps) * 1000)
                e_t_ms = int(((r["end_frame"] / fps) - 0.1) * 1000)
                e_t_ms = max(0, e_t_ms)
                
                filter_str += f"sine=f=1000:d=0.1,adelay={s_t_ms}|{s_t_ms}[s{i}];"
                filter_str += f"sine=f=1000:d=0.1,adelay={e_t_ms}|{e_t_ms}[e{i}];"
                inputs.append(f"[s{i}]")
                inputs.append(f"[e{i}]")
            
            if results and not self.stop_requested:
                filter_str += "".join(inputs) + f"amix=inputs={len(inputs)}:normalize=0[aout]"
                tone_cmd.extend(["-filter_complex", filter_str, "-map", "[aout]"])
            
            tone_cmd.append(temp_audio)
            
            if not self.stop_requested:
                try:
                    subprocess.run(tone_cmd, check=True, capture_output=True)
                    self.log.emit("Audio tones generated.")
                except subprocess.CalledProcessError as e:
                    self.log.emit(f"FFmpeg Audio Error: {e.stderr.decode()}")
                    subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=stereo:d={duration}", temp_audio], check=True)

            self.progress.emit(75 if mode == "both" else 100)

        if self.stop_requested:
            if os.path.exists(temp_video): os.remove(temp_video)
            if os.path.exists(temp_audio): os.remove(temp_audio)
            return

        # 3. Muxing
        self.log.emit("Finalizing output file...")
        final_cmd = ["ffmpeg", "-y"]
        
        if mode == "video":
            final_cmd.extend(["-i", temp_video, "-c:v", "libx264", "-pix_fmt", "yuv420p", output_path])
        elif mode == "audio":
            final_cmd.extend(["-i", temp_audio, output_path])
        else: # both
            final_cmd.extend(["-i", temp_video, "-i", temp_audio, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", output_path])

        if not self.stop_requested:
            try:
                subprocess.run(final_cmd, check=True, capture_output=True)
                self.log.emit(f"Marker file created successfully: {output_path}")
            except subprocess.CalledProcessError as e:
                self.log.emit(f"FFmpeg Muxing Error: {e.stderr.decode()}")
            finally:
                if os.path.exists(temp_video): os.remove(temp_video)
                if os.path.exists(temp_audio): os.remove(temp_audio)

        self.progress.emit(100)

    def _resize_to_fit(self, img, width, height):
        h, w = img.shape[:2]
        ratio = min(width/w, height/h)
        new_w, new_h = int(w * ratio), int(h * ratio)
        resized = cv2.resize(img, (new_w, new_h))
        
        canvas = np.zeros((height, width, 3), np.uint8)
        x_offset = (width - new_w) // 2
        y_offset = (height - new_h) // 2
        canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
        return canvas
