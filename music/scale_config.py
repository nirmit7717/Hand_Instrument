NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
FREQUENCIES = {}

# Generate universal mapping across wide pitch spread (Octaves 2 - 6)
for octave in range(2, 7):
    for i, note in enumerate(NOTES):
        midi_number = 12 * (octave + 1) + i
        freq = 440.0 * (2.0 ** ((midi_number - 69) / 12.0))
        FREQUENCIES[f"{note}{octave}"] = round(freq, 2)

DEFAULT_OCTAVE = 4
