# Track bugfix_linux_file_picker_regression_20260218 Implementation Plan

## Phase 1: Investigation and Logging [checkpoint: 330fd31]
- [x] Task: Add Debug Logging to File Selection (82ce777)
    - [x] Add `print` or `add_log` statements in `add_videos` and `add_images` to see the output of `QFileDialog.getOpenFileNames`.
    - [x] Have the user run the application and report the logs.
- [x] Task: Test with Non-Native Dialog (940029a)
    - [x] Apply `QFileDialog.Option.DontUseNativeDialog` and check if it resolves the issue.

## Phase 2: Implementation and Verification [checkpoint: 4d3d34b]
- [x] Task: Refine File Filter Handling (d2b6646)
    - [x] Ensure the file filter string follows the most compatible format for Linux pickers.
- [x] Task: Improve Robustness of Path Handling (d2b6646)
    - [x] Add checks for file existence and handle potential URL formats if they appear.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Implementation and Verification'
