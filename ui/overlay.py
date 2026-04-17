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
        self.font_medium = pygame.font.SysFont('Segoe UI', 16, bold=True)
        self.font_small = pygame.font.SysFont('Segoe UI', 12, bold=True)
        
        self.keys_layout = [
            ("A", -1), ("A#", -1), ("B", -1),
            ("C", 0), ("C#", 0), ("D", 0), ("D#", 0), ("E", 0), ("F", 0), ("F#", 0), ("G", 0), ("G#", 0), ("A", 0), ("A#", 0), ("B", 0),
            ("C", 1), ("C#", 1), ("D", 1), ("D#", 1), ("E", 1)
        ]
        
        self.piano_w = 600
        self.piano_h = 160
        self.piano_x = (self.width - self.piano_w) // 2
        self.piano_y = self.height - self.piano_h - 20

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

    def get_hitboxes(self, current_octave):
        hitboxes = {}
        
        btn_w, btn_h = 90, 40
        hitboxes["SYS_OCT_DOWN"] = {"rect": pygame.Rect(20, 20, btn_w, btn_h), "type": "sys", "label": "< OCT"}
        hitboxes["SYS_OCT_UP"] = {"rect": pygame.Rect(130, 20, btn_w, btn_h), "type": "sys", "label": "OCT >"}
        hitboxes["SYS_INST"] = {"rect": pygame.Rect(240, 20, int(btn_w * 1.5), btn_h), "type": "sys", "label": "SWITCH INST"}
        
        drag_bar_h = 24
        drag_rect = pygame.Rect(self.piano_x, self.piano_y - drag_bar_h, self.piano_w, drag_bar_h)
        hitboxes["SYS_DRAG"] = {"rect": drag_rect, "type": "drag"}
        
        white_keys = [k for k in self.keys_layout if "#" not in k[0]]
        total_white = len(white_keys)
        
        key_w = self.piano_w // total_white
        self.piano_w = key_w * total_white 
        
        white_index = 0
        for note, offset in self.keys_layout:
            note_name = f"{note}{current_octave + offset}"
            if "#" not in note:
                rect = pygame.Rect(self.piano_x + (white_index * key_w), self.piano_y, key_w, self.piano_h)
                hitboxes[note_name] = {"rect": rect, "type": "white"}
                white_index += 1
                
        white_index = 0
        for note, offset in self.keys_layout:
            note_name = f"{note}{current_octave + offset}"
            if "#" in note:
                bw = int(key_w * 0.6)
                bh = int(self.piano_h * 0.6)
                bx = int(self.piano_x + (white_index * key_w) - (bw / 2))
                rect = pygame.Rect(bx, self.piano_y, bw, bh)
                hitboxes[note_name] = {"rect": rect, "type": "black"}
            else:
                white_index += 1

        return hitboxes

    def draw_ui(self, surface, hitboxes, active_pinches, pressed_keys, instrument):
        for name, data in hitboxes.items():
            if data["type"] == "sys":
                rect = data["rect"]
                is_active = name in active_pinches
                color = (100, 255, 100, 200) if is_active else (40, 40, 50, 200)
                
                btn_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                pygame.draw.rect(btn_surface, color, btn_surface.get_rect(), border_radius=5)
                pygame.draw.rect(btn_surface, (200, 200, 200), btn_surface.get_rect(), width=2, border_radius=5)
                surface.blit(btn_surface, rect.topleft)
                
                label_color = (0, 0, 0) if is_active else (255, 255, 255)
                label = self.font_medium.render(data["label"], True, label_color)
                surface.blit(label, label.get_rect(center=rect.center))

        inst_label = self.font_medium.render(f"Playing: {instrument.upper()}", True, (50, 255, 200))
        surface.blit(inst_label, (self.width - inst_label.get_width() - 20, 30))

        if "SYS_DRAG" in hitboxes:
            rect = hitboxes["SYS_DRAG"]["rect"]
            color = (80, 80, 200, 200) if "SYS_DRAG" in active_pinches else (60, 60, 80, 200)
            bar_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.rect(bar_surface, color, bar_surface.get_rect(), border_top_left_radius=8, border_top_right_radius=8)
            surface.blit(bar_surface, rect.topleft)
            drag_lbl = self.font_small.render("Pinch here to Drag Keyboard", True, (255, 255, 255))
            surface.blit(drag_lbl, drag_lbl.get_rect(center=rect.center))

        for name, data in hitboxes.items():
            if data["type"] == "white":
                rect = data["rect"]
                is_active = name in pressed_keys
                color = (150, 255, 150) if is_active else (240, 240, 240)
                pygame.draw.rect(surface, color, rect)
                pygame.draw.rect(surface, (20, 20, 20), rect, width=2)
                label = self.font_small.render(name, True, (0, 0, 0))
                surface.blit(label, (rect.centerx - label.get_width()//2, rect.bottom - 20))
                
        for name, data in hitboxes.items():
            if data["type"] == "black":
                rect = data["rect"]
                is_active = name in pressed_keys
                color = (100, 255, 100) if is_active else (30, 30, 30)
                pygame.draw.rect(surface, color, rect)
                pygame.draw.rect(surface, (0, 0, 0), rect, width=2)
                label = self.font_small.render(name, True, (255, 255, 255))
                surface.blit(label, (rect.centerx - label.get_width()//2, rect.bottom - 20))
