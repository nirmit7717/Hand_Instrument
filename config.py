# config.py

# Video Configuration
CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
TARGET_FPS = 30

# Gesture Thresholds
# For finger bending detection (using z-distance, or simple distance)
# MediaPipe hand landmarks have 21 points
FINGER_BEND_THRESHOLD = 0.8
# Swipe parameters
SWIPE_VELOCITY_THRESHOLD = 0.05 # normalized coordinates per frame
SWIPE_FRAME_WINDOW = 5

# Audio / Debounce Configuration
DEBOUNCE_TIME = 0.150 # 150 milliseconds
