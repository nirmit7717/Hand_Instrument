import numpy as np
import pygame

def apply_adsr(wave, sample_rate, attack=0.05, decay=0.2, sustain_level=0.3, release=0.3):
    """Applies an ADSR envelope to a waveform to prevent clipping and generate natural dynamics."""
    n_samples = len(wave)
    envelope = np.zeros(n_samples)
    
    a_samples = int(attack * sample_rate)
    d_samples = int(decay * sample_rate)
    r_samples = int(release * sample_rate)
    s_samples = max(0, n_samples - a_samples - r_samples)
    
    current_idx = 0
    
    if a_samples > 0:
        actual_a = min(a_samples, n_samples)
        envelope[current_idx:current_idx+actual_a] = np.linspace(0.0, 1.0, actual_a)
        current_idx += actual_a
        
    if d_samples > 0 and current_idx < n_samples:
        actual_d = min(d_samples, n_samples - current_idx)
        envelope[current_idx:current_idx+actual_d] = np.linspace(1.0, sustain_level, actual_d)
        current_idx += actual_d
        
    if s_samples > 0 and current_idx < n_samples:
        actual_s = min(s_samples, n_samples - current_idx - r_samples)
        if actual_s > 0:
            envelope[current_idx:current_idx+actual_s] = sustain_level
            current_idx += actual_s
        
    if r_samples > 0 and current_idx < n_samples:
        actual_r = n_samples - current_idx
        start_level = envelope[current_idx-1] if current_idx > 0 else 1.0
        envelope[current_idx:current_idx+actual_r] = np.linspace(start_level, 0.0, actual_r)
        
    return wave * envelope

def apply_echo(wave, sample_rate, delay_ms=200, decay=0.4):
    """Applies a simple delay buffer echo effect."""
    delay_samples = int(sample_rate * (delay_ms / 1000.0))
    echo = wave * decay
    padded_wave = np.pad(wave, (0, delay_samples), 'constant')
    padded_echo = np.pad(echo, (delay_samples, 0), 'constant')
    return padded_wave + padded_echo


def generate_instrument_wave(instrument_type, frequency, duration=1.5, volume=0.5, sample_rate=44100):
    """Generates rich harmonic layers based on the selected instrument class."""
    n_samples = int(round(duration * sample_rate))
    t = np.linspace(0, duration, n_samples, False)
    
    wave = np.zeros(n_samples)
    
    if instrument_type == "Electric Piano":
        wave += np.sin(2 * np.pi * frequency * t) * 1.0
        wave += np.sin(2 * np.pi * frequency * 2 * t) * 0.4
        wave += np.sin(2 * np.pi * frequency * 3 * t) * 0.2
        wave += np.sin(2 * np.pi * frequency * 4 * t) * 0.1
        wave = apply_adsr(wave, sample_rate, attack=0.01, decay=0.3, sustain_level=0.1, release=0.8)
        
    elif instrument_type == "Synth Brass":
        for i in range(1, 8):
            wave += (1.0 / i) * np.sin(2 * np.pi * frequency * i * t)
        wave = apply_adsr(wave, sample_rate, attack=0.1, decay=0.2, sustain_level=0.7, release=0.4)
        
    elif instrument_type == "Vibraphone":
        wave += np.sin(2 * np.pi * frequency * t) * 1.0
        wave += np.sin(2 * np.pi * frequency * 4 * t) * 0.3
        wave = apply_adsr(wave, sample_rate, attack=0.02, decay=0.6, sustain_level=0.1, release=1.0)
        wave = apply_echo(wave, sample_rate, delay_ms=150, decay=0.3)
        
    elif instrument_type == "Ambient Pad":
        wave += np.sin(2 * np.pi * frequency * t) * 0.5
        wave += np.sin(2 * np.pi * (frequency * 1.01) * t) * 0.4
        wave += np.sin(2 * np.pi * (frequency * 0.5) * t) * 0.6
        # Apply Tremolo (LFO)
        lfo = 0.5 + 0.5 * np.sin(2 * np.pi * 3.0 * t) 
        wave = wave * lfo
        wave = apply_adsr(wave, sample_rate, attack=0.4, decay=0.1, sustain_level=0.9, release=1.5)
        wave = apply_echo(wave, sample_rate, delay_ms=400, decay=0.5)

    
    else:
        wave = np.sin(2 * np.pi * frequency * t)
        wave = apply_adsr(wave, sample_rate, attack=0.05, decay=0.1, sustain_level=0.5, release=0.2)
        
    max_val = np.max(np.abs(wave))
    if max_val > 0: wave = wave / max_val
        
    wave = wave * 32767 * volume
    stereo_wave = np.column_stack((wave.astype(np.int16), wave.astype(np.int16)))
    return pygame.sndarray.make_sound(stereo_wave)
