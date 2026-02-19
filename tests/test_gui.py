import unittest
from PyQt6.QtWidgets import QApplication, QMainWindow, QListWidget, QPushButton, QVBoxLayout, QWidget, QStatusBar
from src.gui import MainWindow
import sys

# Need a global app instance for PyQt tests
app = QApplication(sys.argv)

class TestGuiLayout(unittest.TestCase):
    def setUp(self):
        self.window = MainWindow()

    def test_window_title(self):
        self.assertEqual(self.window.windowTitle(), "Frame Detector")

    def test_widgets_exist(self):
        # Check for key components
        self.assertIsInstance(self.window.video_list, QListWidget)
        self.assertIsInstance(self.window.image_list, QListWidget)
        self.assertIsInstance(self.window.add_video_btn, QPushButton)
        self.assertIsInstance(self.window.add_image_btn, QPushButton)
        self.assertIsInstance(self.window.start_btn, QPushButton)
        self.assertIsInstance(self.window.pause_btn, QPushButton)
        self.assertIsInstance(self.window.resume_btn, QPushButton)
        self.assertIsInstance(self.window.stop_btn, QPushButton)
        self.assertIsInstance(self.window.gen_video_btn, QPushButton)
        self.assertIsInstance(self.window.gen_audio_btn, QPushButton)
        self.assertIsInstance(self.window.gen_both_btn, QPushButton)
        self.assertIsInstance(self.window.cancel_marker_btn, QPushButton)
        self.assertIsInstance(self.window.status_bar, QStatusBar)

    def test_add_videos_logic(self):
        # Mocking QFileDialog.getOpenFileNames and os.path.exists
        from unittest.mock import patch
        with patch('PyQt6.QtWidgets.QFileDialog.getOpenFileNames', return_value=(['video1.mp4', 'video2.mp4'], '')), \
             patch('os.path.exists', return_value=True):
            self.window.add_videos()
            self.assertEqual(len(self.window.videos), 2)
            self.assertEqual(self.window.video_list.count(), 2)

    def test_add_images_logic(self):
        from unittest.mock import patch
        with patch('PyQt6.QtWidgets.QFileDialog.getOpenFileNames', return_value=(['image1.png'], '')), \
             patch('os.path.exists', return_value=True):
            self.window.add_images()
            self.assertEqual(len(self.window.images), 1)
            # The key is now an absolute path because of os.path.abspath
            import os
            abs_path = os.path.abspath('image1.png')
            self.assertIn(abs_path, self.window.images)
            self.assertEqual(self.window.image_list.count(), 1)
            self.assertEqual(self.window.images[abs_path], 'image1.png')

    def test_edit_alias_logic(self):
        from unittest.mock import patch
        import os
        # Setup initial image
        with patch('PyQt6.QtWidgets.QFileDialog.getOpenFileNames', return_value=(['image1.png'], '')), \
             patch('os.path.exists', return_value=True):
            self.window.add_images()
        
        abs_path = os.path.abspath('image1.png')
        item = self.window.image_list.item(0)
        with patch('PyQt6.QtWidgets.QInputDialog.getText', return_value=('new_alias', True)):
            self.window.edit_alias(item)
            self.assertEqual(self.window.images[abs_path], 'new_alias')
            self.assertIn('new_alias', item.text())

    def test_update_progress(self):
        import time
        self.window.start_time = time.time() - 10
        self.window.update_progress(50)
        # We need to wait for animation or check end value
        self.assertEqual(self.window.progress_animation.endValue(), 50)
        self.assertIn("Elapsed", self.window.time_label.text())

    def test_add_log(self):
        self.window.add_log("Test log message")
        self.assertIn("Test log message", self.window.log_view.toPlainText())

    def test_start_processing_empty(self):
        self.window.start_processing()
        self.assertIn("Error: Please add at least one video and one target image.", self.window.log_view.toPlainText())

    def test_processing_finished_enables_buttons(self):
        # Mock results: target -> list of ranges
        results = {
            "target1": [
                {"start_frame": 10, "end_frame": 15, "start_time": 1.0, "end_time": 1.5, "video": "v1.mp4"}
            ]
        }
        self.window.processing_finished(results)
        self.assertTrue(self.window.gen_video_btn.isEnabled())
        self.assertTrue(self.window.gen_audio_btn.isEnabled())
        self.assertTrue(self.window.gen_both_btn.isEnabled())

    def test_display_results(self):
        # Mock results: target -> list of ranges
        results = {
            "target1": [
                {"start_frame": 10, "end_frame": 15, "start_time": 1.0, "end_time": 1.5, "video": "v1.mp4"},
                {"start_frame": 50, "end_frame": 55, "start_time": 5.0, "end_time": 5.5, "video": "v1.mp4"}
            ]
        }
        self.window.display_results(results)
        
        # Check table contents
        self.assertEqual(self.window.results_table.rowCount(), 2)
        self.assertEqual(self.window.results_table.item(0, 0).text(), "v1.mp4")
        self.assertEqual(self.window.results_table.item(0, 1).text(), "target1")
        self.assertEqual(self.window.results_table.item(0, 2).text(), "1.00 - 1.50")
        self.assertEqual(self.window.results_table.item(0, 3).text(), "10 - 15")

if __name__ == "__main__":
    unittest.main()

if __name__ == "__main__":
    unittest.main()
