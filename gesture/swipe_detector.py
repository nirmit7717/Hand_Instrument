from config import SWIPE_VELOCITY_THRESHOLD, SWIPE_FRAME_WINDOW

class SwipeDetector:
    def __init__(self):
        self.history = []
        self.max_history = SWIPE_FRAME_WINDOW

    def update_and_detect(self, landmarks):
        if not landmarks:
            self.history.clear()
            return None

        # Wrist as center
        wrist = landmarks[0]
        center = (wrist[0], wrist[1])
        
        self.history.append(center)
        if len(self.history) > self.max_history:
            self.history.pop(0)
            
        if len(self.history) == self.max_history:
            start_x, start_y = self.history[0]
            end_x, end_y = self.history[-1]
            
            dx = end_x - start_x
            dy = end_y - start_y
            
            if abs(dx) > abs(dy) and abs(dx) > SWIPE_VELOCITY_THRESHOLD:
                self.history.clear()
                return "Right" if dx > 0 else "Left"
            elif abs(dy) > abs(dx) and abs(dy) > SWIPE_VELOCITY_THRESHOLD:
                self.history.clear()
                return "Down" if dy > 0 else "Up"
                
        return None
