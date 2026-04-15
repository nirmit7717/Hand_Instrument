from gesture.finger_detector import FingerDetector

class GestureLogic:
    def __init__(self):
        self.finger_detector = FingerDetector()

    def process_hands(self, hands_data):
        gesture_state = {
            "Left": {},
            "Right": {}
        }
        
        for hand in hands_data:
            hand_type = hand["type"]
            landmarks = hand["landmarks"]
            
            finger_states = self.finger_detector.detect_fingers(landmarks)
            gesture_state[hand_type] = finger_states
                    
        return gesture_state
