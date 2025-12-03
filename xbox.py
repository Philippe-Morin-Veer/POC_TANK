from evdev import InputDevice, categorize, ecodes
import threading
import time

class XboxController:
    def __init__(self, device_path="/dev/input/event4"):
        self.device_path = device_path
        self.gamepad = None
        self.connected = False
        self.values = {
            "ABS_Y": 32767,
            "ABS_RZ": 32767,
        }

        self.new_event = False   # <<< NOUVEAU FLAG
        self.running = False
        self.thread = None

    def _open_device(self):
        try:
            self.gamepad = InputDevice(self.device_path)
            self.connected = True
            print(f"[Xbox] Manette détectée : {self.device_path}")
            return True
        except:
            self.connected = False
            return False

    def _read_loop(self):
        if not self._open_device():
            print("[Xbox] Aucune manette trouvée.")
            return

        while self.running:
            try:
                for event in self.gamepad.read_loop():

                    if not self.running:
                        break

                    if event.type == ecodes.EV_ABS:
                        absevent = categorize(event)
                        code = ecodes.ABS[absevent.event.code]
                        value = absevent.event.value

                        if code in self.values:
                            self.values[code] = value
                            self.new_event = True       # <<< NOUVEAU : événement réel

                    time.sleep(0.001)

            except OSError:
                print("[Xbox] Manette déconnectée")
                self.connected = False

                self.values = {
                    "ABS_Y": 32767,
                    "ABS_RZ": 32767,
                }
                time.sleep(0.5)

                while self.running and not self._open_device():
                    time.sleep(1)

            except Exception as e:
                print(f"[Xbox] Erreur inconnue : {e}")

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._read_loop, daemon=True)
            self.thread.start()

    def stop(self):
        self.running = False

    def get_values(self):
        if not self.connected:
            return None
        return dict(self.values)

    def pop_new_event(self):  # <<< MÉTHODE AJOUTÉE
        if self.new_event:
            self.new_event = False
            return True
        return False

    def convert_to_percent(self, value):
        mid = 32767
        if value == mid:
            return 0
        if value < mid:
            return int((mid - value) / mid * 100)
        else:
            return int(-((value - mid) / mid) * 100)
