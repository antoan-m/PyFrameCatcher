import unittest
import numpy as np
from src.matcher import FrameMatcher

class TestFrameMatcher(unittest.TestCase):
    def setUp(self):
        self.matcher = FrameMatcher(threshold=0.05)

    def test_compare_identical_images(self):
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        self.assertTrue(self.matcher.compare(img, img))

    def test_compare_different_images(self):
        img1 = np.zeros((100, 100, 3), dtype=np.uint8)
        img2 = np.ones((100, 100, 3), dtype=np.uint8) * 255
        self.assertFalse(self.matcher.compare(img1, img2))

    def test_compare_different_shapes(self):
        img1 = np.zeros((100, 100, 3), dtype=np.uint8)
        img2 = np.zeros((50, 50, 3), dtype=np.uint8)
        self.assertTrue(self.matcher.compare(img1, img2))

    def test_group_consecutive_frames(self):
        # frames: (frame_number, timestamp)
        self.assertEqual(self.matcher.group_matches([]), [])

        matches = [
            (10, 1.0), (11, 1.1), (12, 1.2),
            (20, 2.0),
            (30, 3.0), (31, 3.1)
        ]
        expected = [
            {"start_frame": 10, "end_frame": 12, "start_time": 1.0, "end_time": 1.2},
            {"start_frame": 20, "end_frame": 20, "start_time": 2.0, "end_time": 2.0},
            {"start_frame": 30, "end_frame": 31, "start_time": 3.0, "end_time": 3.1}
        ]
        result = self.matcher.group_matches(matches)
        self.assertEqual(result, expected)

if __name__ == "__main__":
    unittest.main()
