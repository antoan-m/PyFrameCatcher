# Product Requirements

## User Stories (MVP)
- **As a user,** I want to upload a video and a screenshot so I can see if the frame exists in the video.
- **As a user,** I want to add multiple screenshots with aliases and see which ones are found across multiple videos.
- **As a user,** I want to view a progress bar and a live log while the analysis is running.
- **As a user,** I want to export the detection results to a CSV or JSON file.

## Functional Requirements
- **Frame Matching:**
    - Support for exact match and high-similarity match (configurable tolerance).
    - Accurate conversion between frame numbers and wall-clock timestamps.
    - Detection and grouping of consecutive matching frames into ranges to avoid duplicate noise.
- **Performance:**
    - Multi-threaded processing to prevent GUI freezing during heavy scans.
    - Efficient usage of FFmpeg and OpenCV for frame extraction and comparison.

## Non-Functional Requirements
- **Performance:** The tool should process videos efficiently, aiming for faster-than-real-time speeds where possible.
- **Usability:** The GUI should remain responsive and provide clear feedback (progress bars, logs) at all times.
- **Portability:** The application must run without complex installation on **Windows, macOS, and Linux**.
- **Reliability:** The application should handle corrupt video files or unsupported formats gracefully without crashing.
