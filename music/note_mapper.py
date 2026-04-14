from config import DEBOUNCE_TIME
from utils.debounce import Debouncer

class NoteMapper:
    def __init__(self):
        self.debouncer = Debouncer(DEBOUNCE_TIME)
        
        self.finger_to_note_base_right = {
            "Thumb": "C",
            "Index": "D",
            "Middle": "E",
            "Ring": "F",
            "Pinky": "G"
        }

        self.finger_to_note_base_left = {
            "Thumb": "A",
            "Index": "B",
            "Middle": "C", 
            "Ring": "D",
            "Pinky": "E"
        }

    def get_triggered_notes(self, gesture_state, current_octave):
        notes_to_play = []

        if "Right" in gesture_state:
            for finger_name, is_bent in gesture_state["Right"].items():
                if is_bent:
                    base_note = self.finger_to_note_base_right.get(finger_name)
                    if base_note:
                        full_note = f"{base_note}{current_octave}"
                        debounce_key = f"Right_{finger_name}"
                        if self.debouncer.can_trigger(debounce_key):
                            notes_to_play.append(full_note)

        if "Left" in gesture_state:
            # We can map left hand to one octave lower
            left_octave = current_octave - 1 if current_octave > 3 else 3
            for finger_name, is_bent in gesture_state["Left"].items():
                if is_bent:
                    base_note = self.finger_to_note_base_left.get(finger_name)
                    if base_note:
                        full_note = f"{base_note}{left_octave}"
                        debounce_key = f"Left_{finger_name}"
                        if self.debouncer.can_trigger(debounce_key):
                            notes_to_play.append(full_note)

        return notes_to_play
