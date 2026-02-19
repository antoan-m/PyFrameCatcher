import unittest
from PyQt6.QtWidgets import QApplication
from src.gui import MainWindow
import sys
import os
import json
import csv
from unittest.mock import patch

# Need a global app instance for PyQt tests
app = QApplication.instance() or QApplication(sys.argv)

class TestExportFunctionality(unittest.TestCase):
    def setUp(self):
        self.window = MainWindow()
        self.results = {
            "target1": [
                {
                    "start_frame": 10, "end_frame": 15, 
                    "start_time": 1.0, "end_time": 1.5,
                    "video": "video1.mp4"
                }
            ]
        }
        self.window.last_results = self.results
        self.window.display_results(self.results)
        self.test_csv = "test_export.csv"
        self.test_json = "test_export.json"

    def tearDown(self):
        if os.path.exists(self.test_csv):
            os.remove(self.test_csv)
        if os.path.exists(self.test_json):
            os.remove(self.test_json)

    def test_export_buttons_exist(self):
        self.assertTrue(hasattr(self.window, 'export_csv_btn'))
        self.assertTrue(hasattr(self.window, 'export_json_btn'))

    def test_export_csv(self):
        with patch('PyQt6.QtWidgets.QFileDialog.getSaveFileName', return_value=(self.test_csv, '')):
            self.window.export_csv()
        
        self.assertTrue(os.path.exists(self.test_csv))
        with open(self.test_csv, 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
            self.assertEqual(rows[0], ["Video", "Target Alias", "Start Time (s)", "End Time (s)", "Start Frame", "End Frame"])
            self.assertEqual(rows[1], ["video1.mp4", "target1", "1.00", "1.50", "10", "15"])

    def test_export_json(self):
        with patch('PyQt6.QtWidgets.QFileDialog.getSaveFileName', return_value=(self.test_json, '')):
            self.window.export_json()
        
        self.assertTrue(os.path.exists(self.test_json))
        with open(self.test_json, 'r') as f:
            data = json.load(f)
            self.assertEqual(data["target1"][0]["video"], "video1.mp4")
            self.assertEqual(data["target1"][0]["start_frame"], 10)

if __name__ == "__main__":
    unittest.main()
