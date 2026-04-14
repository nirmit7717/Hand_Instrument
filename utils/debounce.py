import time

class Debouncer:
    def __init__(self, debounce_time=0.150):
        self.debounce_time = debounce_time
        self.last_triggered = {}

    def can_trigger(self, key):
        current_time = time.time()
        if key not in self.last_triggered or (current_time - self.last_triggered[key]) >= self.debounce_time:
            self.last_triggered[key] = current_time
            return True
        return False
