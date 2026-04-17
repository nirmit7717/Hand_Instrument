"""
MIDI Handler — Real-time MIDI event emission and session recording.

Broadcasts NOTE_ON / NOTE_OFF events over a virtual MIDI port (requires loopMIDI
on Windows or a system virtual port on macOS/Linux). Also records timed events
and exports them as a standard .mid file using mido.
"""
import time
import threading
from music.scale_config import FREQUENCIES

try:
    import mido
    from mido import MidiFile, MidiTrack, Message
    MIDO_AVAILABLE = True
except ImportError:
    MIDO_AVAILABLE = False
    print("[MidiHandler] mido not installed — MIDI output disabled.")


def _note_name_to_midi(note_name: str) -> int:
    """Convert a note name like 'C4' or 'F#3' into a MIDI number (0-127)."""
    NOTE_MAP = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4,
                "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}
    # Split note letter(s) from octave digit
    if len(note_name) >= 2 and note_name[-1].isdigit():
        octave = int(note_name[-1])
        note = note_name[:-1]
        if note in NOTE_MAP:
            return 12 * (octave + 1) + NOTE_MAP[note]
    return -1


class MidiHandler:
    def __init__(self):
        self.port = None
        self.recording = False
        self.session_events = []   # [(delta_ms, type, note_name)]
        self._record_start = None
        self._last_event_time = None
        self._lock = threading.Lock()

        if MIDO_AVAILABLE:
            self._try_open_port()

    def _try_open_port(self):
        """Attempt to open the first available MIDI output port."""
        try:
            available = mido.get_output_names()
            if available:
                self.port = mido.open_output(available[0])
                print(f"[MidiHandler] Connected to MIDI port: {available[0]}")
            else:
                print("[MidiHandler] No MIDI output ports found. Export-only mode.")
        except Exception as e:
            print(f"[MidiHandler] Failed to open MIDI port: {e}")

    # -------------------------------------------------------------------------
    # Real-time MIDI Output
    # -------------------------------------------------------------------------
    def note_on(self, note_name: str, velocity: int = 100):
        midi_num = _note_name_to_midi(note_name)
        if midi_num < 0:
            return
        if self.port and MIDO_AVAILABLE:
            self.port.send(mido.Message("note_on", note=midi_num, velocity=velocity))
        if self.recording:
            self._record_event("note_on", note_name)

    def note_off(self, note_name: str):
        midi_num = _note_name_to_midi(note_name)
        if midi_num < 0:
            return
        if self.port and MIDO_AVAILABLE:
            self.port.send(mido.Message("note_off", note=midi_num, velocity=0))
        if self.recording:
            self._record_event("note_off", note_name)

    # -------------------------------------------------------------------------
    # Session Recording
    # -------------------------------------------------------------------------
    def start_recording(self):
        with self._lock:
            self.session_events = []
            self.recording = True
            self._record_start = time.time()
            self._last_event_time = self._record_start
        print("[MidiHandler] Recording started.")

    def stop_recording(self):
        with self._lock:
            self.recording = False
        print(f"[MidiHandler] Recording stopped. {len(self.session_events)} events captured.")

    def _record_event(self, event_type: str, note_name: str):
        now = time.time()
        with self._lock:
            delta_ms = int((now - self._last_event_time) * 1000)
            self._last_event_time = now
            self.session_events.append((delta_ms, event_type, note_name))

    # -------------------------------------------------------------------------
    # Export to .mid File
    # -------------------------------------------------------------------------
    def export_to_file(self, filepath: str = "session.mid"):
        if not MIDO_AVAILABLE:
            print("[MidiHandler] mido not available — cannot export.")
            return
        if not self.session_events:
            print("[MidiHandler] No events to export.")
            return

        ticks_per_beat = 480
        tempo = 500000  # 120 BPM in microseconds per beat
        ms_per_tick = tempo / (ticks_per_beat * 1000)

        mid = MidiFile(ticks_per_beat=ticks_per_beat)
        track = MidiTrack()
        mid.tracks.append(track)
        track.append(mido.MetaMessage("set_tempo", tempo=tempo, time=0))

        with self._lock:
            events = list(self.session_events)

        for delta_ms, event_type, note_name in events:
            midi_num = _note_name_to_midi(note_name)
            if midi_num < 0:
                continue
            ticks = int(delta_ms / ms_per_tick)
            velocity = 100 if event_type == "note_on" else 0
            track.append(Message(event_type, note=midi_num, velocity=velocity, time=ticks))

        mid.save(filepath)
        print(f"[MidiHandler] Session exported to '{filepath}' ({len(events)} events).")
        return filepath

    def close(self):
        if self.port:
            self.port.close()
