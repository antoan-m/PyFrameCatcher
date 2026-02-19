import cv2
import numpy as np

class FrameMatcher:
    def __init__(self, threshold=0.05):
        """
        threshold: maximum allowed difference ratio (0.0 to 1.0)
        """
        self.threshold = threshold

    def compare(self, img1, img2):
        """
        Compares two images and returns True if they are similar within the threshold.
        """
        if img1.shape != img2.shape:
            # Resize img2 to match img1 if shapes differ
            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

        # Simple pixel-wise difference
        diff = cv2.absdiff(img1, img2)
        non_zero_count = np.count_nonzero(diff)
        total_pixels = img1.size
        
        # Calculate mean difference
        # Alternatively, use mean squared error or similar
        # For simplicity, let's use the average difference per pixel
        mean_diff = np.mean(diff) / 255.0
        
        return mean_diff <= self.threshold

    def group_matches(self, matches):
        """
        Groups consecutive matching frames into ranges.
        matches: list of (frame_number, timestamp)
        returns: list of dicts with start/end frame/time
        """
        if not matches:
            return []

        ranges = []
        start_frame, start_time = matches[0]
        prev_frame, prev_time = matches[0]

        for i in range(1, len(matches)):
            curr_frame, curr_time = matches[i]
            if curr_frame == prev_frame + 1:
                prev_frame, prev_time = curr_frame, curr_time
            else:
                ranges.append({
                    "start_frame": start_frame,
                    "end_frame": prev_frame,
                    "start_time": start_time,
                    "end_time": prev_time
                })
                start_frame, start_time = curr_frame, curr_time
                prev_frame, prev_time = curr_frame, curr_time

        ranges.append({
            "start_frame": start_frame,
            "end_frame": prev_frame,
            "start_time": start_time,
            "end_time": prev_time
        })

        return ranges
