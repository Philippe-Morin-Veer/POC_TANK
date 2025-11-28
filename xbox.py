from evdev import InputDevice, categorize, ecodes
import threading
import time

class XboxController:
    def __init__(self, device_path="/dev/input/event4"):
        self.device_path = device_path
        self.gamepad = None

        self.values = {
            "ABS_X": 0,
            "ABS_Y": 0,
            "ABS_Z": 0,
            "ABS_RZ": 0,
            "BTN_TR": 0,
        }

        self.running = False
        self.thread = None

    def _read_loop(self):
        """Boucle de lecture continue."""
        try:
            self.gamepad = InputDevice(self.device_path)
            print(f"Manette détectée sur {self.device_path}")
        except Exception as e:
            print(f"ERREUR : impossible d'ouvrir {self.device_path} -> {e}")
            self.running = False
            return

        for event in self.gamepad.read_loop():
            if not self.running:
                break

            if event.type == ecodes.EV_ABS:
                absevent = categorize(event)
                code = ecodes.ABS[absevent.event.code]
                value = absevent.event.value

                if code in self.values:
                    self.values[code] = value

            time.sleep(0.001)

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._read_loop, daemon=True)
            self.thread.start()

    def stop(self):
        self.running = False

    def get_values(self):
        return dict(self.values)
