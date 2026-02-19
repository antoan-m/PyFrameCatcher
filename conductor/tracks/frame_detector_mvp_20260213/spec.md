# Track frame_detector_mvp_20260213 Specification

## Overview
This track focuses on delivering the MVP of the Frame Detector application. The core objective is to allow users to identify specific frames (defined by screenshots) within video files and report their occurrences (timestamps/frame numbers).

## Key Features
- **GUI (PyQt6/PySide6):**
    - File selection for multiple videos.
    - Image selection for multiple target screenshots with alias naming.
    - Progress bars (global and per-file).
    - Live log view for real-time feedback.
    - Interactive results table with export options (CSV/JSON).
- **Processing Engine (OpenCV/FFmpeg):**
    - Background threading (QThread) for non-blocking analysis.
    - Frame extraction and comparison logic.
    - Tolerance-based matching (~5% similarity).
    - Grouping of consecutive matching frames into ranges.
- **Output:**
    - Console output.
    - Log file generation.
    - Structured export.

## Technical Requirements
- Python 3.8+
- PyQt6 or PySide6
- OpenCV (`opencv-python`)
- FFmpeg (System binary or bundled)
- PyInstaller for packaging
