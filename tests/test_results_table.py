import unittest
from PyQt6.QtWidgets import QApplication, QTableWidget
from src.gui import MainWindow
import sys

# Need a global app instance for PyQt tests
app = QApplication.instance() or QApplication(sys.argv)

class TestResultsTable(unittest.TestCase):
    def setUp(self):
        self.window = MainWindow()

    def test_table_has_video_column(self):
        # We want 4 columns: Video, Target Alias, Time Range, Frame Range
        self.assertEqual(self.window.results_table.columnCount(), 4)
        self.assertEqual(self.window.results_table.horizontalHeaderItem(0).text(), "Video")
        self.assertEqual(self.window.results_table.horizontalHeaderItem(1).text(), "Target Alias")

    def test_display_results_with_video(self):
        results = {
            "target1": [
                {
                    "start_frame": 10, "end_frame": 15, 
                    "start_time": 1.0, "end_time": 1.5,
                    "video": "video1.mp4"
                }
            ]
        }
        self.window.display_results(results)
        
        self.assertEqual(self.window.results_table.rowCount(), 1)
        self.assertEqual(self.window.results_table.item(0, 0).text(), "video1.mp4")
        self.assertEqual(self.window.results_table.item(0, 1).text(), "target1")

    def test_table_is_sortable(self):
        self.assertTrue(self.window.results_table.isSortingEnabled())

if __name__ == "__main__":
    unittest.main()
