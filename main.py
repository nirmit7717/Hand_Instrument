import cv2
import time
import numpy as np
import pygame
import os
import warnings

# Silence common Mediapipe/TF warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings("ignore", category=UserWarning, module='google.protobuf.symbol_database')

from config import CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT, TARGET_FPS

from vision.camera import Camera
from vision.hand_tracker import HandTracker
from gesture.spatial_detector import SpatialDetector
from music.instrument_manager import InstrumentManager
from audio.audio_engine import AudioEngine
from ui.overlay import Overlay
from ui.visualizer import AudioVisualizer
from utils.debounce import Debouncer
from utils.event_bus import event_bus
from utils.state import app_state
from music.midi_handler import MidiHandler
from gesture.ml_classifier import GestureClassifier

def main():
    try:
        camera = Camera(CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT)
    except Exception as e:
        print(f"Error accessing camera: {e}")
        return
        
    pygame.init()
    screen = pygame.display.set_mode((FRAME_WIDTH, FRAME_HEIGHT))
    pygame.display.set_caption("Hyper-Optimized AR Piano")
    clock = pygame.time.Clock()

    hand_tracker = HandTracker()
    spatial_detector = SpatialDetector(FRAME_WIDTH, FRAME_HEIGHT)
    
    audio_engine = AudioEngine()
    instrument_manager = InstrumentManager(audio_engine)
    overlay = Overlay(FRAME_WIDTH, FRAME_HEIGHT)
    midi_handler = MidiHandler()
    gesture_classifier = GestureClassifier()
    visualizer = AudioVisualizer(
        x=FRAME_WIDTH - 220, y=80, width=210, height=100
    )
    system_debouncer = Debouncer(debounce_time=0.8)

    print("Starting Optimized UI. Hover to play keys, Pinch top bar to Drag! ESC to quit.")

    running = True
    
    is_dragging = False
    drag_offset_x = 0
    drag_offset_y = 0

    while running:
        frame = camera.read_frame()
        if frame is None:
            print("Failed to read camera sequence")
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Exiting: QUIT event received")
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    print("Exiting: ESC key pressed")
                    running = False

        try:
            hands_data = hand_tracker.process_frame(frame)
        except Exception as e:
            print(f"Error processing frame: {e}")
            break
        overlay.draw_landmarks(frame, hands_data)

        hitboxes = overlay.get_hitboxes(instrument_manager.current_octave)
        
        eval_state = spatial_detector.evaluate_hands(hands_data, hitboxes)
        active_pinches = eval_state["pinches"]
        pressed_keys = eval_state["pressed_keys"]
        pinch_coords = eval_state["pinch_coords"]

        # Physics Drag Engine
        if "SYS_DRAG" in active_pinches and len(pinch_coords) > 0:
            cursor_x, cursor_y = pinch_coords[0]
            if not is_dragging:
                is_dragging = True
                drag_offset_x = cursor_x - overlay.piano_x
                drag_offset_y = cursor_y - overlay.piano_y
            else:
                overlay.piano_x = np.clip(cursor_x - drag_offset_x, 0, FRAME_WIDTH - overlay.piano_w)
                overlay.piano_y = np.clip(cursor_y - drag_offset_y, 0, FRAME_HEIGHT)
        else:
            is_dragging = False

        # System UI Handlers
        if "SYS_OCT_DOWN" in active_pinches and system_debouncer.can_trigger("sys_oct_dn"):
            instrument_manager.shift_octave(up=False)
        if "SYS_OCT_UP" in active_pinches and system_debouncer.can_trigger("sys_oct_up"):
            instrument_manager.shift_octave(up=True)
        if "SYS_INST" in active_pinches and system_debouncer.can_trigger("sys_inst"):
            instrument_manager.toggle_instrument(up=True)

        # Audio Loop executing via Event Bus + MIDI
        for note in eval_state.get("note_on", []):
            event_bus.publish("NOTE_ON", note)
            midi_handler.note_on(note)
        for note in eval_state.get("note_off", []):
            event_bus.publish("NOTE_OFF", note)
            midi_handler.note_off(note)

        # ML Gesture Classification (per-hand macro actions)
        for hand in hands_data:
            gesture = gesture_classifier.predict(hand["landmarks"])
            if gesture == "FIST" and system_debouncer.can_trigger("ml_fist"):
                if not midi_handler.recording:
                    midi_handler.start_recording()
                    app_state.is_recording = True
                else:
                    midi_handler.stop_recording()
                    midi_handler.export_to_file("session.mid")
                    app_state.is_recording = False

        # Update + draw visualizer
        visualizer.update(pressed_keys, instrument_manager.current_instrument)

        # Pygame Rendering Optimized - Traded out swapping Numpy Arrays dynamically
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_transposed = cv2.transpose(frame_rgb)
        frame_surf = pygame.surfarray.make_surface(frame_transposed)

        overlay.draw_ui(frame_surf, hitboxes, active_pinches, pressed_keys, instrument_manager.current_instrument)
        visualizer.draw(frame_surf)

        # Recording indicator
        if app_state.is_recording:
            rec_font = pygame.font.SysFont("Segoe UI", 14, bold=True)
            rec_label = rec_font.render("● REC", True, (255, 60, 60))
            frame_surf.blit(rec_label, (10, FRAME_HEIGHT - 30))

        screen.blit(frame_surf, (0, 0))
        pygame.display.flip()
        
        # Audio rendering runs asynchronously so we can tick faster if needed
        clock.tick(TARGET_FPS)

    print("Shutting down... cleaning up resources.")
    midi_handler.close()
    camera.release()
    audio_engine.quit()
    pygame.quit()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[{e}] Fatal error. Ensuring cleanly stopped.")
        # Best effort cleanup
        pygame.quit()
        cv2.destroyAllWindows()
