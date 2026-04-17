import math

class SpatialDetector:
    def __init__(self, width=640, height=480):
        self.width = width
        self.height = height
        
        self.fingertips = [4, 8, 12, 16, 20]
        self.PINCH_THRESHOLD = 0.05
        
        self.previous_pressed_keys = set()

    def evaluate_hands(self, hands_data, hitboxes):
        result = {
            "pinches": set(),
            "pressed_keys": set(),
            "pinch_coords": []
        }
        
        is_globally_dragging = False
        
        # Pass 1: Identify if ANY hand is pinching the SYS_DRAG handle.
        # This allows us to globally mute piano inputs during layout movements.
        for hand in hands_data:
            landmarks = hand["landmarks"]
            t_tip = landmarks[4]
            i_tip = landmarks[8]
            
            dist = math.dist((t_tip[0], t_tip[1]), (i_tip[0], i_tip[1]))
            if dist < self.PINCH_THRESHOLD:
                px = int(((t_tip[0] + i_tip[0]) / 2.0) * self.width)
                py = int(((t_tip[1] + i_tip[1]) / 2.0) * self.height)
                
                # Check system/drag collisions exclusively
                for key_name, data in hitboxes.items():
                    if data["type"] in ["sys", "drag"]:
                        if data["rect"].collidepoint(px, py):
                            result["pinches"].add(key_name)
                            if key_name == "SYS_DRAG":
                                is_globally_dragging = True
                            if data["type"] == "drag":
                                result["pinch_coords"].append((px, py))
                                
        # Pass 2: Evaluate pure physical bounding-box entries for the keyboard.
        # If we are dragging the keyboard, we explicitly mute entry checks to avert Midas touch!
        if not is_globally_dragging:
            for hand in hands_data:
                landmarks = hand["landmarks"]
                for tip_idx in self.fingertips:
                    tip = landmarks[tip_idx]
                    px = int(tip[0] * self.width)
                    py = int(tip[1] * self.height)
                    
                    hit_something = False
                    for pass_classes in [["black"], ["white"]]:
                        if hit_something: break
                        
                        for key_name, data in hitboxes.items():
                            if data["type"] in pass_classes:
                                if data["rect"].collidepoint(px, py):
                                    result["pressed_keys"].add(key_name)
                                    hit_something = True
                                    break
                                    
        new_pressed = result["pressed_keys"]
        result["note_on"] = list(new_pressed - self.previous_pressed_keys)
        result["note_off"] = list(self.previous_pressed_keys - new_pressed)
        self.previous_pressed_keys = new_pressed
        
        result["pinches"] = list(result["pinches"])
        result["pressed_keys"] = list(new_pressed)
        return result
