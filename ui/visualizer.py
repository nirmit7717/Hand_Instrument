"""
Audio Visualizer — renders a real-time frequency bar chart + oscilloscope
directly onto the Pygame surface as a HUD panel.

Since we use synthesized waveforms (not microphone input), we simulate the
frequency spectrum from the currently active notes and their instrument types,
driving a visually rich animated display.
"""
import math
import pygame
import numpy as np


class AudioVisualizer:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.NUM_BARS = 32
        self.bar_w = width // self.NUM_BARS
        self.bar_peaks = [0.0] * self.NUM_BARS  # peak hold values
        self.bar_vals = [0.0] * self.NUM_BARS   # current bar heights (smoothed)
        self.DECAY = 0.85        # bars fall at this rate per frame
        self.PEAK_DECAY = 0.97   # peak dots fall slower

        # Oscilloscope sine buffer (composite of all active notes)
        self.oscilloscope_points = []
        self._frame = 0

        pygame.font.init()
        self._font = pygame.font.SysFont("Segoe UI", 11, bold=True)

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------
    def update(self, active_note_names: list, instrument: str):
        """
        Drive visualizer from active note names.
        Maps notes → frequencies → bar magnitudes.
        """
        self._frame += 1
        target_bars = [0.0] * self.NUM_BARS

        for note_name in active_note_names:
            freq = self._note_to_freq(note_name)
            if freq <= 0:
                continue
            # Map frequency logarithmically to bar index
            bar_idx = self._freq_to_bar(freq)
            if 0 <= bar_idx < self.NUM_BARS:
                harmonics = self._get_harmonics(instrument)
                for harmonic, gain in harmonics:
                    h_idx = min(bar_idx + harmonic, self.NUM_BARS - 1)
                    target_bars[h_idx] = min(1.0, target_bars[h_idx] + gain)

        # Smooth bars
        for i in range(self.NUM_BARS):
            self.bar_vals[i] = max(target_bars[i], self.bar_vals[i] * self.DECAY)
            self.bar_peaks[i] = max(self.bar_vals[i], self.bar_peaks[i] * self.PEAK_DECAY)

        # Build oscilloscope from composite sine wave
        self._update_oscilloscope(active_note_names)

    def draw(self, surface: pygame.Surface):
        """Draw the full visualizer panel onto the surface."""
        panel_h_bars = int(self.height * 0.6)
        panel_h_osc = self.height - panel_h_bars

        # Draw semi-transparent background
        panel = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        panel.fill((10, 10, 20, 180))
        pygame.draw.rect(panel, (50, 50, 80, 220), panel.get_rect(), width=1, border_radius=6)
        surface.blit(panel, (self.x, self.y))

        # Draw frequency bars
        self._draw_bars(surface, self.x, self.y, self.width, panel_h_bars)

        # Draw oscilloscope
        self._draw_oscilloscope(surface, self.x, self.y + panel_h_bars, self.width, panel_h_osc)

        # Label
        lbl = self._font.render("SPECTRUM", True, (100, 180, 255))
        surface.blit(lbl, (self.x + 4, self.y + 2))

    # -------------------------------------------------------------------------
    # Internal Rendering
    # -------------------------------------------------------------------------
    def _draw_bars(self, surface, x, y, w, h):
        margin = 2
        for i in range(self.NUM_BARS):
            bx = x + i * self.bar_w + margin
            val = self.bar_vals[i]
            bar_height = int(val * (h - 8))

            # Gradient color: blue → cyan → green → yellow at peaks
            hue_start = 200  # blue in HSL degrees approximated with RGB
            r = int(min(255, (val ** 0.5) * 500))
            g = int(100 + val * 155)
            b = int(255 - val * 200)
            color = (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))

            bar_rect = pygame.Rect(bx, y + h - bar_height - 4, self.bar_w - margin * 2, bar_height)
            if bar_height > 0:
                pygame.draw.rect(surface, color, bar_rect, border_radius=2)

            # Peak dot
            peak_y = y + h - int(self.bar_peaks[i] * (h - 8)) - 4
            if self.bar_peaks[i] > 0.05:
                pygame.draw.rect(surface, (255, 255, 255),
                                 pygame.Rect(bx, peak_y - 2, self.bar_w - margin * 2, 2))

    def _draw_oscilloscope(self, surface, x, y, w, h):
        if len(self.oscilloscope_points) < 2:
            return
        mid_y = y + h // 2
        pts = []
        for i, val in enumerate(self.oscilloscope_points):
            px = x + int(i * w / len(self.oscilloscope_points))
            py = int(mid_y + val * (h // 2 - 4))
            pts.append((px, py))
        if len(pts) >= 2:
            pygame.draw.lines(surface, (0, 220, 180), False, pts, 2)

    def _update_oscilloscope(self, note_names):
        samples = 64
        composite = np.zeros(samples)
        t = np.linspace(0, 1, samples)
        drift = self._frame * 0.05

        for note in note_names:
            freq = self._note_to_freq(note)
            if freq > 0:
                composite += np.sin(2 * math.pi * (freq / 100.0) * t + drift)

        if len(note_names) > 0:
            cmax = np.max(np.abs(composite)) + 1e-6
            composite = composite / cmax
        self.oscilloscope_points = composite.tolist()

    # -------------------------------------------------------------------------
    # Frequency Mapping
    # -------------------------------------------------------------------------
    NOTE_MAP = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4,
                "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}

    def _note_to_freq(self, note_name: str) -> float:
        try:
            octave = int(note_name[-1])
            note = note_name[:-1]
            midi = 12 * (octave + 1) + self.NOTE_MAP.get(note, -1)
            if midi < 0:
                return 0.0
            return 440.0 * (2.0 ** ((midi - 69) / 12.0))
        except Exception:
            return 0.0

    def _freq_to_bar(self, freq: float) -> int:
        """Map a frequency to a bar index using a log scale (20Hz – 8000Hz)."""
        f_min, f_max = 20.0, 8000.0
        if freq <= f_min:
            return 0
        log_ratio = math.log(freq / f_min) / math.log(f_max / f_min)
        return int(log_ratio * self.NUM_BARS)

    def _get_harmonics(self, instrument: str):
        """Return list of (bar_offset, gain) for each instrument's harmonic profile."""
        if instrument == "Electric Piano":
            return [(0, 1.0), (2, 0.4), (4, 0.2), (6, 0.1)]
        elif instrument == "Synth Brass":
            return [(i, 1.0 / (i + 1)) for i in range(7)]
        elif instrument == "Vibraphone":
            return [(0, 1.0), (6, 0.3)]
        elif instrument == "Ambient Pad":
            return [(0, 0.5), (1, 0.4), (-2, 0.3), (3, 0.2), (5, 0.15)]
        return [(0, 1.0)]
