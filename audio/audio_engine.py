import pygame
from utils.event_bus import event_bus

class AudioEngine:
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.mixer.init()
        pygame.init()
        
        self.sounds = {}
        self.active_channels = {}
        pygame.mixer.set_num_channels(32)
        
        event_bus.subscribe("NOTE_ON", self.play_note)
        event_bus.subscribe("NOTE_OFF", self.stop_note)

    def load_sounds(self, note_dict):
        self.sounds = note_dict

    def play_note(self, note_name):
        if note_name in self.sounds:
            channel = pygame.mixer.find_channel()
            if channel:
                channel.play(self.sounds[note_name])
                self.active_channels[note_name] = channel

    def stop_note(self, note_name):
        if note_name in self.active_channels:
            self.active_channels[note_name].fadeout(150)
            del self.active_channels[note_name]

    def quit(self):
        pygame.quit()
