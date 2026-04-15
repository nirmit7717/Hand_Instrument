import cv2
import mediapipe as mp
import pygame

class Overlay:
    def __init__(self, width=640, height=480):
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.mp_hands = mp.solutions.hands
        self.width = width
        self.height = height
        
        pygame.font.init()
        self.font_large = pygame.font.SysFont('Segoe UI', 32, bold=True)
        self.font_medium = pygame.font.SysFont('Segoe UI', 22, bold=True)
        self.font_small = pygame.font.SysFont('Segoe UI', 16)

    def draw_landmarks(self, frame, hands_data):
        for hand in hands_data:
            if "raw_landmarks" in hand:
                self.mp_drawing.draw_landmarks(
                    frame,
                    hand["raw_landmarks"],
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style()
                )

    def draw_dashboard(self, surface, instrument, octave):
        panel_rect = pygame.Rect(self.width - 240, 20, 220, 120)
        panel_surface = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (25, 25, 30, 210), panel_surface.get_rect(), border_radius=12)
        surface.blit(panel_surface, panel_rect.topleft)

        title = self.font_small.render("SETTINGS DASHBOARD", True, (150, 150, 160))
        inst_label = self.font_medium.render(instrument.upper(), True, (0, 255, 150))
        octave_label = self.font_medium.render(f"OCTAVE: {octave}", True, (255, 180, 50))
        
        surface.blit(title, (self.width - 220, 35))
        surface.blit(inst_label, (self.width - 220, 65))
        surface.blit(octave_label, (self.width - 220, 100))

    def draw_piano(self, surface, triggered_notes, current_octave):
        key_width = 80
        key_height = 100
        start_x = (self.width - (key_width * 7)) // 2
        start_y = self.height - key_height - 20
        
        notes = ["C", "D", "E", "F", "G", "A", "B"]
        
        for i, note in enumerate(notes):
            full_note = f"{note}{current_octave}"
            rect = pygame.Rect(start_x + (i * key_width), start_y, key_width - 8, key_height)
            
            is_active = full_note in triggered_notes
            color = (255, 255, 255, 200) if not is_active else (50, 255, 100, 255)
            
            key_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.rect(key_surface, color, key_surface.get_rect(), border_radius=8)
            pygame.draw.rect(key_surface, (80, 80, 80, 255), key_surface.get_rect(), width=3, border_radius=8)
            surface.blit(key_surface, rect.topleft)
            
            label = self.font_large.render(note, True, (20, 20, 20))
            label_rect = label.get_rect(center=rect.center)
            surface.blit(label, label_rect)
