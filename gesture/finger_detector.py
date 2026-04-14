import math

# Finger angle threshold in degrees. 
# A perfectly straight finger is ~180 degrees. 
# Bending it slightly drops the angle. 160 degrees makes it very sensitive.
FINGER_BEND_ANGLE_THRESHOLD = 155

class FingerDetector:
    def __init__(self):
        # Indices: (Vertex/Middle joint, Top joint, Bottom joint) 
        # to calculate angle naturally.
        self.finger_indices = {
            "Thumb":  (2, 4, 1),   # angle at MCP between Tip and CMC
            "Index":  (6, 8, 5),   # angle at PIP between Tip and MCP
            "Middle": (10, 12, 9),
            "Ring":   (14, 16, 13),
            "Pinky":  (18, 20, 17)
        }

    def _calculate_angle(self, p1, p2, p3):
        # p2 is the vertex
        v1 = [p1[0] - p2[0], p1[1] - p2[1], p1[2] - p2[2]]
        v2 = [p3[0] - p2[0], p3[1] - p2[1], p3[2] - p2[2]]
        
        dot_product = sum(i*j for i, j in zip(v1, v2))
        mag1 = math.sqrt(sum(i**2 for i in v1))
        mag2 = math.sqrt(sum(i**2 for i in v2))
        
        if mag1 * mag2 == 0:
            return 0
        
        cos_angle = dot_product / (mag1 * mag2)
        cos_angle = max(min(cos_angle, 1.0), -1.0)
        angle = math.acos(cos_angle)
        return math.degrees(angle)

    def is_bent(self, vertex_idx, tip_idx, base_idx, landmarks):
        vertex = landmarks[vertex_idx]
        tip = landmarks[tip_idx]
        base = landmarks[base_idx]
        
        angle = self._calculate_angle(tip, vertex, base)
        
        # Trigger if the finger flexes (bends) more than the threshold
        return angle < FINGER_BEND_ANGLE_THRESHOLD

    def detect_fingers(self, landmarks):
        finger_states = {}
        for name, (vertex_idx, tip_idx, base_idx) in self.finger_indices.items():
            finger_states[name] = self.is_bent(vertex_idx, tip_idx, base_idx, landmarks)
            
        return finger_states
