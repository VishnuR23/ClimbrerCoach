import mediapipe as mp
import numpy as np

class PoseTracker:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(static_image_mode=False, model_complexity=1, enable_segmentation=False)

    def process(self, frame_bgr):
        h, w = frame_bgr.shape[:2]
        image_rgb = frame_bgr[:, :, ::-1]
        res = self.pose.process(image_rgb)
        if not res.pose_landmarks:
            return None
        pts = []
        for lm in res.pose_landmarks.landmark:
            pts.append((int(lm.x * w), int(lm.y * h)))
        return pts

    @staticmethod
    def get_named(pts):
        # MediaPipe indices
        idx = {
            "left_wrist": 15, "right_wrist": 16,
            "left_ankle": 27, "right_ankle": 28,
            "left_hip": 23, "right_hip": 24,
            "left_shoulder": 11, "right_shoulder": 12,
        }
        out = {}
        if pts is None: return out
        for k, i in idx.items():
            if 0 <= i < len(pts):
                out[k] = pts[i]
        return out
