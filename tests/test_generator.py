import unittest
import os
import cv2
import numpy as np
from src.generator import MarkerGenerator

class TestMarkerGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = MarkerGenerator()
        self.test_video = "test_source.mp4"
        self.test_image = "test_target.png"
        self.output_video = "test_markers.mp4"
        
        # Create a dummy video
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(self.test_video, fourcc, 30.0, (640, 480))
        for _ in range(60): # 2 seconds
            frame = np.zeros((480, 640, 3), np.uint8)
            out.write(frame)
        out.release()
        
        # Create a dummy image
        img = np.ones((100, 100, 3), np.uint8) * 255
        cv2.imwrite(self.test_image, img)

    def tearDown(self):
        for f in [self.test_video, self.test_image, self.output_video]:
            if os.path.exists(f):
                os.remove(f)

    def test_video_properties(self):
        props = self.generator.get_video_properties(self.test_video)
        self.assertEqual(props["width"], 640)
        self.assertEqual(props["height"], 480)
        self.assertEqual(props["fps"], 30.0)
        self.assertEqual(props["total_frames"], 60)

    def test_marker_generation_video_only(self):
        results = [
            {"start_frame": 10, "end_frame": 20, "target_path": self.test_image}
        ]
        self.generator.create_marker_file(self.test_video, results, self.output_video, mode="video")
        
        self.assertTrue(os.path.exists(self.output_video))
        cap = cv2.VideoCapture(self.output_video)
        self.assertEqual(int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), 60)
        
        # Check a frame that should be black
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret, frame = cap.read()
        self.assertTrue(ret)
        self.assertEqual(np.mean(frame), 0)
        
        # Check a frame that should have the image
        cap.set(cv2.CAP_PROP_POS_FRAMES, 15)
        ret, frame = cap.read()
        self.assertTrue(ret)
        self.assertGreater(np.mean(frame), 0)
        
        cap.release()

    def test_marker_generation_audio_only(self):
        results = [
            {"start_frame": 10, "end_frame": 20, "target_path": self.test_image}
        ]
        self.generator.create_marker_file(self.test_video, results, self.output_video, mode="audio")
        self.assertTrue(os.path.exists(self.output_video))
        # Basic check: file is non-empty
        self.assertGreater(os.path.getsize(self.output_video), 0)

    def test_marker_generation_both(self):
        results = [
            {"start_frame": 10, "end_frame": 20, "target_path": self.test_image}
        ]
        self.generator.create_marker_file(self.test_video, results, self.output_video, mode="both")
        self.assertTrue(os.path.exists(self.output_video))
        # Basic check: file is non-empty
        self.assertGreater(os.path.getsize(self.output_video), 0)

if __name__ == "__main__":
    unittest.main()
