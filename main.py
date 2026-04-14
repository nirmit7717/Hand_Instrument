import cv2
import time
import numpy as np
import pygame
from config import CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT, TARGET_FPS

from vision.camera import Camera
from vision.hand_tracker import HandTracker
from gesture.gesture_logic import GestureLogic
from music.note_mapper import NoteMapper
from music.instrument_manager import InstrumentManager
from audio.audio_engine import AudioEngine
from ui.overlay import Overlay
from utils.debounce import Debouncer

def main():
    try:
        camera = Camera(CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT)
    except Exception as e:
        print(f"Error accessing camera: {e}")
        return
        
    pygame.init()
    screen = pygame.display.set_mode((FRAME_WIDTH, FRAME_HEIGHT))
    pygame.display.set_caption("Hand-Controlled Musical Instrument")
    clock = pygame.time.Clock()

    hand_tracker = HandTracker()
    gesture_logic = GestureLogic()
    note_mapper = NoteMapper()
    
    audio_engine = AudioEngine()
    instrument_manager = InstrumentManager(audio_engine)
    overlay = Overlay(FRAME_WIDTH, FRAME_HEIGHT)
    
    swipe_debouncer = Debouncer(debounce_time=0.8)

    print("Starting Pygame Instrument. Press ESC to quit.")

    running = True
    last_swipe = ""

    while running:
        frame = camera.read_frame()
        if frame is None:
            print("Failed to read frame")
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        hands_data = hand_tracker.process_frame(frame)
        gesture_state = gesture_logic.process_hands(hands_data)
        
        overlay.draw_landmarks(frame, hands_data)

        swipe = gesture_state.get("swipe")
        if swipe and swipe_debouncer.can_trigger("swipe"):
            last_swipe = swipe
            if swipe == "Right":
                instrument_manager.shift_octave(up=True)
            elif swipe == "Left":
                instrument_manager.shift_octave(up=False)
            elif swipe == "Up":
                instrument_manager.toggle_instrument(up=True)
            elif swipe == "Down":
                instrument_manager.toggle_instrument(up=False)

        notes_to_play = note_mapper.get_triggered_notes(gesture_state, instrument_manager.current_octave)
        
        for note in notes_to_play:
            audio_engine.play_note(note)

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_surf = pygame.surfarray.make_surface(np.swapaxes(frame_rgb, 0, 1))

        overlay.draw_dashboard(frame_surf, instrument_manager.current_instrument, instrument_manager.current_octave, last_swipe)
        overlay.draw_piano(frame_surf, notes_to_play, instrument_manager.current_octave)

        screen.blit(frame_surf, (0, 0))
        pygame.display.flip()
        
        clock.tick(TARGET_FPS)

    camera.release()
    audio_engine.quit()
    pygame.quit()

if __name__ == "__main__":
    main()
