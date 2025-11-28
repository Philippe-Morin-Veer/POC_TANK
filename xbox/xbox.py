from inputs import get_gamepad
import time
import threading

class XboxController:
    def __init__(self):
        """Initialisation de la manette Xbox."""
        self.values = {
            "ABS_X": 0,
            "ABS_Y": 0,
            "ABS_RX": 0,
            "ABS_RY": 0,
            # Ajout possible de boutons ici
        }

        self.running = False
        self.thread = None

    def _read_loop(self):
        """Boucle qui lit constamment les événements de la manette."""
        while self.running:
            events = get_gamepad()
            for event in events:
                if event.ev_type == "Absolute":
                    if event.code in self.values:
                        self.values[event.code] = event.state
                elif event.ev_type == "Key":
                    self.values[event.code] = event.state

            time.sleep(0.01)  # éviter de monopoliser le CPU

    def start(self):
        """Lance la lecture de la manette en arrière-plan."""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._read_loop, daemon=True)
            self.thread.start()

    def stop(self):
        """Arrête la lecture de la manette."""
        self.running = False
        if self.thread:
            self.thread.join()

    def get_values(self):
        """Retourne les dernières valeurs connues."""
        return dict(self.values)
