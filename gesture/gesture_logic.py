from gesture.finger_detector import FingerDetector
from gesture.swipe_detector import SwipeDetector

class GestureLogic:
    def __init__(self):
        self.finger_detector = FingerDetector()
        self.swipe_detector = SwipeDetector()

    def process_hands(self, hands_data):
        gesture_state = {
            "Left": {},
            "Right": {},
            "swipe": None
        }
        
        for hand in hands_data:
            hand_type = hand["type"]
            landmarks = hand["landmarks"]
            
            finger_states = self.finger_detector.detect_fingers(landmarks)
            gesture_state[hand_type] = finger_states
            
            # Only detect swipe from Right hand for simpler interaction, or rightmost
            if hand_type == "Right":
                swipe = self.swipe_detector.update_and_detect(landmarks)
                if swipe:
                    gesture_state["swipe"] = swipe
                    
        return gesture_state
