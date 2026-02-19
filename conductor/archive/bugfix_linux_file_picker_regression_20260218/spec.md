# Specification: Fix Linux File Picker Regression

## Problem Statement
After a Linux update, users report that selecting video and image files through the GUI does not result in the files being added to the application lists. No error message is shown, and the application remains functional but unusable for new analysis.

## Analysis
- `QFileDialog.getOpenFileNames` is likely returning an empty list, a list of URLs (instead of paths), or the filter argument is interfering with newer system-native file pickers.
- Common fixes for Linux Qt file dialog issues include:
    - Forcing the non-native dialog (`Options.DontUseNativeDialog`).
    - Verifying if returned paths are correctly parsed.
    - Testing with different filter formats.

## Goals
- Ensure file selection works consistently on Linux.
- Add robust logging to identify why file selection might fail.
- Improve error reporting if file selection fails.

## Success Criteria
- Files can be selected and added to the application on Linux.
- Automated tests (mocked) continue to pass.
- Manual verification on the user's system confirms the fix.
