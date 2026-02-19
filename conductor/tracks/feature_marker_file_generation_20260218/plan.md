# Track feature_marker_file_generation_20260218 Implementation Plan

## Phase 1: Core Engine for Marker Generation [checkpoint: f4565be]
- [x] Task: Marker Generator Logic
    - [x] Implement a `MarkerGenerator` class.
    - [x] Add methods to extract video properties (FPS, resolution, duration).
    - [x] Implement frame-by-frame black video creation with image insertion.
    - [x] Implement audio tone generation using FFmpeg.
- [x] Task: Muxing and Output
    - [x] Combine video and audio streams using FFmpeg.
    - [x] Handle video-only and audio-only output modes.

## Phase 2: GUI Integration [checkpoint: adfb8cd]
- [x] Task: Marker Generation Dialog
    - [x] Create a dialog to select output mode (Video/Audio/Both) and save path.
- [x] Task: Integrate with Results Table
    - [x] Add "Generate Markers" button to the GUI.
    - [x] Connect the button to the generation logic, passing the current detection results.
    - [x] Add progress feedback for the generation process.

## Phase 3: Verification and Polish [checkpoint: 5a8e3d2]
- [x] Task: Unit Tests for Marker Generation (adfb8cd)
- [x] Task: Bugfix: FFmpeg sine filter option 't' not found (f4565be)
    - [x] Fixed FFmpeg command to use `adelay` and `amix`.
- [x] Task: UI Refinement: Direct Buttons (e2a3b4c)
    - [x] Replaced dialog with 3 direct buttons for Video, Audio, and Both.
- [x] Task: Final UX Polish (9f8a7b6)
    - [x] Add Cancel button for marker generation.
    - [x] Add Time Elapsed / Remaining tracking.
    - [x] Add completion sound.
    - [x] Add status bar with version, author, and GitHub link.
- [x] Task: Conductor - User Manual Verification 'Marker File Generation'
