"""
ML Gesture Classifier — KNN-based hand pose recognition.

Encodes 21 normalized MediaPipe hand landmarks (63 features: x, y, z per point)
and classifies named macro poses: "FIST", "OPEN_PALM", "PEACE", "POINT_UP".

Usage:
  classifier = GestureClassifier()
  classifier.record_sample(landmarks, label="FIST")  # collect training data
  classifier.train()
  gesture = classifier.predict(landmarks)             # returns label or None
"""
import os
import json
import numpy as np

try:
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import Pipeline
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("[GestureClassifier] scikit-learn not installed — ML gestures disabled.")


# Pre-baked training samples (hand-labeled heuristics encoded as landmark vectors)
# Each sample is a flat 63-element list: [x0,y0,z0, x1,y1,z1, ... x20,y20,z20]
# relative to wrist (landmark 0).
_BUILTIN_DATA_FILE = os.path.join(os.path.dirname(__file__), "gesture_data.json")


class GestureClassifier:
    LABELS = ["FIST", "OPEN_PALM", "PEACE", "POINT_UP"]

    def __init__(self, k: int = 5):
        self.k = k
        self.model = None
        self.training_X = []
        self.training_y = []
        self._load_saved_data()
        if len(self.training_X) >= self.k:
            self.train()

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------
    @staticmethod
    def _encode(landmarks) -> np.ndarray:
        """
        Flatten landmarks relative to wrist and normalize by hand span.
        Input: list of (x, y, z) tuples — 21 landmarks.
        Returns: 1-D numpy array of length 63.
        """
        pts = np.array([(lm[0], lm[1], lm[2]) for lm in landmarks], dtype=np.float32)
        wrist = pts[0]
        pts -= wrist  # translate so wrist is origin
        span = np.linalg.norm(pts[9] - wrist) + 1e-6  # palm span for scale
        pts /= span
        return pts.flatten()

    def _load_saved_data(self):
        if os.path.exists(_BUILTIN_DATA_FILE):
            try:
                with open(_BUILTIN_DATA_FILE, "r") as f:
                    data = json.load(f)
                self.training_X = [d["features"] for d in data]
                self.training_y = [d["label"] for d in data]
                print(f"[GestureClassifier] Loaded {len(self.training_X)} saved samples.")
            except Exception as e:
                print(f"[GestureClassifier] Failed to load data: {e}")

    def _save_data(self):
        data = [{"features": self.training_X[i], "label": self.training_y[i]}
                for i in range(len(self.training_X))]
        try:
            with open(_BUILTIN_DATA_FILE, "w") as f:
                json.dump(data, f)
        except Exception as e:
            print(f"[GestureClassifier] Failed to save data: {e}")

    # -------------------------------------------------------------------------
    # Training Data Collection
    # -------------------------------------------------------------------------
    def record_sample(self, landmarks, label: str):
        """Record one labeled training sample from live landmarks."""
        if label not in self.LABELS:
            print(f"[GestureClassifier] Unknown label '{label}'. Valid: {self.LABELS}")
            return
        features = self._encode(landmarks).tolist()
        self.training_X.append(features)
        self.training_y.append(label)
        self._save_data()
        print(f"[GestureClassifier] Sample recorded for '{label}'. Total: {len(self.training_X)}")

    # -------------------------------------------------------------------------
    # Model Training
    # -------------------------------------------------------------------------
    def train(self):
        if not SKLEARN_AVAILABLE:
            return
        if len(self.training_X) < self.k:
            print(f"[GestureClassifier] Need at least {self.k} samples to train.")
            return
        X = np.array(self.training_X, dtype=np.float32)
        y = self.training_y
        self.model = Pipeline([
            ("scaler", StandardScaler()),
            ("knn", KNeighborsClassifier(n_neighbors=self.k, weights="distance"))
        ])
        self.model.fit(X, y)
        print(f"[GestureClassifier] Model trained on {len(X)} samples.")

    # -------------------------------------------------------------------------
    # Prediction
    # -------------------------------------------------------------------------
    def predict(self, landmarks) -> str | None:
        """
        Predict the gesture label from live 21-point landmarks.
        Returns a label string or None if model not ready or confidence is low.
        """
        if not SKLEARN_AVAILABLE or self.model is None:
            return None
        try:
            features = self._encode(landmarks).reshape(1, -1)
            proba = self.model.predict_proba(features)[0]
            max_proba = np.max(proba)
            if max_proba < 0.6:  # confidence threshold
                return None
            return self.model.classes_[np.argmax(proba)]
        except Exception:
            return None

    def clear_data(self):
        self.training_X = []
        self.training_y = []
        self.model = None
        if os.path.exists(_BUILTIN_DATA_FILE):
            os.remove(_BUILTIN_DATA_FILE)
        print("[GestureClassifier] All training data cleared.")
