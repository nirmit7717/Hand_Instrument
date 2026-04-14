from audio.sound_loader import generate_instrument_wave
from music.scale_config import FREQUENCIES, DEFAULT_OCTAVE

INSTRUMENTS = ["Electric Piano", "Synth Brass", "Vibraphone"]

class InstrumentManager:
    def __init__(self, audio_engine):
        self.current_octave = DEFAULT_OCTAVE
        self.instrument_idx = 0
        self.current_instrument = INSTRUMENTS[self.instrument_idx]
        self.audio_engine = audio_engine
        
        self.load_current_instrument()

    def load_current_instrument(self):
        sounds = {}
        for note_name, freq in FREQUENCIES.items():
            sounds[note_name] = generate_instrument_wave(self.current_instrument, freq, duration=1.5)
        self.audio_engine.load_sounds(sounds)

    def shift_octave(self, up=True):
        changed = False
        if up and self.current_octave < 5:
            self.current_octave += 1
            changed = True
        elif not up and self.current_octave > 3:
            self.current_octave -= 1
            changed = True
        return changed

    def toggle_instrument(self, up=True):
        if up:
            self.instrument_idx = (self.instrument_idx + 1) % len(INSTRUMENTS)
        else:
            self.instrument_idx = (self.instrument_idx - 1) % len(INSTRUMENTS)
        
        self.current_instrument = INSTRUMENTS[self.instrument_idx]
        self.load_current_instrument()
