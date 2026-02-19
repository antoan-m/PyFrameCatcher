# Technology Stack

## Core Language
- **Python:** 3.8+ (Primary Development Language)

## Graphical User Interface (GUI)
- **Framework:** PyQt6 (Modern, robust, and feature-rich)
- **Reasoning:** Offers a professional look and feel, excellent cross-platform support (Windows, macOS, Linux), and powerful threading signals/slots for responsive background processing.

## Video Processing & Computer Vision
- **OpenCV (`opencv-python`):**
    - **Purpose:** Primary library for reading video frames, image processing, and template matching.
    - **Reasoning:** Industry standard for computer vision tasks with optimized performance.
- **FFmpeg (CLI):**
    - **Purpose:** Handling complex video decoding, metadata extraction, and potential preprocessing via subprocess calls.
    - **Reasoning:** Complements OpenCV by handling specialized codecs and container formats that OpenCV's `VideoCapture` might struggle with.

## Concurrency
- **Threading Model:** `QThread` (from PyQt/PySide) or Python's `threading` module.
    - **Purpose:** Offloading intensive video processing and frame matching to background threads to keep the GUI responsive.
    - **Reasoning:** Simplifies communication with the GUI (signals/slots) compared to multiprocessing.

## Packaging & Distribution
- **Tool:** PyInstaller
    - **Purpose:** Bundling the application into standalone executables for Windows (`.exe`), macOS (`.app`/binary), and Linux (binary).
    - **Configuration:** Will include necessary binaries (FFmpeg if feasible, or instructions to install) and assets.
- **Alternative:** Standard Python Package (`setup.py` / `pyproject.toml`) for developers or users preferring `pip install`.
