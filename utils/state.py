class AppState:
    def __init__(self):
        self.is_recording = False
        self.current_octave = 4
        self.active_notes = set()
        self.instrument_loading = False
        self.gesture_mode = "PIANO"
        
app_state = AppState()
