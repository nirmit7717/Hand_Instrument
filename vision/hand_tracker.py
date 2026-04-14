import cv2
import mediapipe as mp

class HandTracker:
    def __init__(self, max_hands=2, detection_con=0.7, tracking_con=0.5):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=detection_con,
            min_tracking_confidence=tracking_con
        )

    def process_frame(self, frame):
        """
        Returns a list of hands with their type (Left/Right) and landmark coordinates.
        Coordinates are normalized to image dimensions [0, 1].
        """
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(img_rgb)
        
        hands_data = []

        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                hand_type = handedness.classification[0].label # "Left" or "Right"
                
                # Convert landmarks to a list of (x, y, z) tuples
                landmarks = [(lm.x, lm.y, lm.z) for lm in hand_landmarks.landmark]
                
                hands_data.append({
                    "type": hand_type,
                    "landmarks": landmarks,
                    "raw_landmarks": hand_landmarks
                })
                
        return hands_data
