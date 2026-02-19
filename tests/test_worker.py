import unittest
from PyQt6.QtCore import QThread, pyqtSignal, QObject
from src.worker import FrameWorker
from unittest.mock import MagicMock
import numpy as np

class TestFrameWorker(unittest.TestCase):
    def test_worker_signals(self):
        # Mock dependencies
        matcher = MagicMock()
        matcher.compare.return_value = True
        matcher.group_matches.return_value = [{"start_frame": 0, "end_frame": 1, "start_time": 0.0, "end_time": 0.1}]
        
        worker = FrameWorker(["video.mp4"], {"image.png": "alias"}, matcher)
        
        # Track signal emissions
        progress_calls = []
        log_calls = []
        finished_calls = []
        
        worker.progress.connect(lambda p: progress_calls.append(p))
        worker.log.connect(lambda l: log_calls.append(l))
        worker.finished.connect(lambda r: finished_calls.append(r))
        
        # We need to mock cv2.VideoCapture to avoid actual file I/O
        with unittest.mock.patch('cv2.VideoCapture') as mock_vc:
            mock_cap = MagicMock()
            mock_vc.return_value = mock_cap
            mock_cap.isOpened.return_value = True
            # Simulate 2 frames
            mock_cap.read.side_effect = [
                (True, np.zeros((10, 10, 3), dtype=np.uint8)),
                (True, np.zeros((10, 10, 3), dtype=np.uint8)),
                (False, None)
            ]
            mock_cap.get.side_effect = lambda prop: 2 if prop == 7 else (0.1 if prop == 0 else 24.0) # 7: FRAME_COUNT, 0: POS_MSEC
            
            with unittest.mock.patch('cv2.imread', return_value=np.zeros((10, 10, 3), dtype=np.uint8)):
                worker.run()
        
        self.assertTrue(len(progress_calls) > 0)
        self.assertTrue(len(log_calls) > 0)
        self.assertEqual(len(finished_calls), 1)
        self.assertIn("alias", finished_calls[0])
        # Verify 'video' key is present and correct
        self.assertEqual(finished_calls[0]["alias"][0]["video"], "video.mp4")

    def test_worker_stop(self):
        matcher = MagicMock()
        worker = FrameWorker(["video.mp4"], {"image.png": "alias"}, matcher)
        worker.stop()
        self.assertFalse(worker._is_running)

if __name__ == "__main__":
    unittest.main()
