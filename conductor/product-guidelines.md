# Product Guidelines

## Visual Aesthetic: "Functional Modernism"
The application will bridge modern minimalist design with the high-information density required for technical video analysis. It will use system-native UI components where possible to ensure a familiar and responsive feel across Windows, macOS, and Linux.

- **Layout:** A clean, multi-pane interface.
    - **Top/Left:** Source selection (Video files and Target Images).
    - **Center:** Real-time processing status and live logs.
    - **Bottom/Right:** Interactive result list with thumbnails and detailed timestamps.
- **Color Palette:** Professional neutral tones (Grays, Whites, or System Dark/Light themes) with high-contrast accent colors for status indicators (e.g., Blue for processing, Green for success, Red for errors).
- **Typography:** Sans-serif system fonts (e.g., Segoe UI, San Francisco, Roboto) for maximum legibility.

## User Interaction & Feedback
- **Progress Communication:**
    - **Global Progress Bar:** Tracks the overall completion of the entire batch.
    - **Per-File Progress Bar:** Detailed progress for the current video file being scanned.
    - **Live Log View:** A scrolling, monospace text area for real-time technical feedback (e.g., "Scanning Frame 4500...", "Match Found at 00:02:15").
- **Target Image Management:**
    - **Thumbnail Grid:** Added screenshots appear as thumbnails.
    - **Inline Aliasing:** Every thumbnail has an immediate, editable text field for its "Alias Name".
- **Result Exploration:**
    - **Interactive List:** Detected frames are listed with their File Name, Alias, Timestamp, and Frame Range.
    - **Visual Verification:** Clicking a result should (if possible) show the detected frame from the video alongside the target screenshot for comparison.

## Tone and Voice
- **Tone:** Professional, Efficient, and Precise.
- **Voice:** The application speaks as a technical tool. Messages should be direct and clear (e.g., "Analysis Complete: 4 matches found in 2 files" instead of "Yay! We found everything!").
- **Error Handling:** Provide technical but actionable error messages (e.g., "Error: FFmpeg not found in system path" or "Unsupported video codec in file.mp4").

## Quality & Accuracy Guidelines
- **Precision:** Reports should always include both the wall-clock timestamp (HH:MM:SS.mmm) and the absolute frame number.
- **Deduplication:** Consecutive frames matching the same target must be grouped into a range (Start - End) to avoid cluttering the output.
- **Concurrency:** The UI must remain responsive during long video scans. Heavy processing (OpenCV/FFmpeg) must occur on background threads.
