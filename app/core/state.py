import threading

class AppState:
    def __init__(self):
        self.is_running = True
        self.data_store = {}
        self._lock = threading.Lock()
        self.executor = None
        self.total_request = 0

    def stop(self):
        with self._lock:
            self.is_running = False

    def increment_request(self):
        with self._lock:
            self.total_request += 1

app_state = AppState()