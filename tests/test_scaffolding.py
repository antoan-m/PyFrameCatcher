import os
import unittest

class TestScaffolding(unittest.TestCase):
    def test_requirements_exists(self):
        self.assertTrue(os.path.exists("requirements.txt") or os.path.exists("pyproject.toml"), "Neither requirements.txt nor pyproject.toml exists")

    def test_src_directory_exists(self):
        self.assertTrue(os.path.exists("src"), "src directory does not exist")

    def test_opencv_installed(self):
        try:
            import cv2
            self.assertTrue(True)
        except ImportError:
            self.fail("OpenCV is not installed")

    def test_ffmpeg_accessible(self):
        # We can check if ffmpeg is in the PATH
        import subprocess
        try:
            subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            self.assertTrue(True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.fail("FFmpeg is not accessible")

if __name__ == "__main__":
    unittest.main()
