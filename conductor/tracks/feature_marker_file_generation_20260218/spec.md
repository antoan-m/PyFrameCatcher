# Specification: Marker File Generation

## Problem Statement
Users want a visual and audible way to identify detected frames when placing analysis results on a video editing timeline. A "marker" file that perfectly matches the source video's length and frame rate is required.

## Proposed Solution
Implement a "Generate Markers" feature that creates a new media file (video, audio, or both).

### Functional Requirements
1.  **Source Video Matching:** The output file must have the same resolution (width/height) and frame rate (FPS) as the source video.
2.  **Video Generation:**
    -   Default: All frames are solid black.
    -   Markers: At timestamps where a target image was detected, replace the black frame with the target image (resized/centered if necessary).
3.  **Audio Generation:**
    -   A low-frequency tone (e.g., 60Hz or 100Hz) should play briefly at the **start** and **end** of every detected frame range.
4.  **Flexible Output:**
    -   User can choose to generate:
        -   Video + Audio (Default)
        -   Only Video
        -   Only Audio
5.  **GUI Integration:**
    -   Add a "Generate Markers" button to the results area.
    -   Provide a dialog or settings pane to select generation options.

### Technical Implementation
-   **OpenCV (`VideoWriter`):** Used to create the video stream frame-by-frame.
-   **FFmpeg (subprocess):** Used to generate the audio tones and mux them with the video stream.
-   **PyQt6:** Used for the UI components and progress feedback.

## Success Criteria
-   Generated video is frame-accurate compared to the source.
-   Target images appear exactly at detected timestamps.
-   Audio tones play at range boundaries.
-   User can select output types (V/A/Both).
