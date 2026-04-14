import pygame

class AudioEngine:
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.mixer.init()
        pygame.init()
        
        self.sounds = {}
        pygame.mixer.set_num_channels(32)

    def load_sounds(self, note_dict):
        self.sounds = note_dict

    def play_note(self, note_name):
        if note_name in self.sounds:
            self.sounds[note_name].play()

    def quit(self):
        pygame.quit()
