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
        self.last_event = time.time()

        self.running = False
        self.thread = None

    def _open_device(self):
        """Ouvre la manette si possible, sinon False."""
        try:
            self.gamepad = InputDevice(self.device_path)
            self.connected = True
            print(f"[Xbox] Manette détectée : {self.device_path}")
            return True
        except:
            self.connected = False
            return False

    def _read_loop(self):
        """Boucle de lecture continue."""
        self.last_event = time.time()
        if not self._open_device():
            print("[Xbox] Aucune manette trouvée.")
            return

        while self.running:
            try:
                self.last_event = time.time()
                # Lecture bloquante
                for event in self.gamepad.read_loop():

                    if not self.running:
                        break

                    if event.type == ecodes.EV_ABS:
                        absevent = categorize(event)
                        code = ecodes.ABS[absevent.event.code]
                        value = absevent.event.value

                        if code in self.values:
                            self.values[code] = value

                    # Petite pause
                    time.sleep(0.001)

            except OSError:
                # Manette débranchée
                print("[Xbox] Manette déconnectée")

                self.connected = False
                self.values = dict(self.neutral_values)  # reset
                time.sleep(0.5)

                # Tentative de reconnexion
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
    
    def convert_to_percent(self, value):
        """Convertit une valeur ABS en pourcentage [-100, 100]."""
        mid = 32767
        if value == mid:
            return 0
        if value < mid:
            return int((mid - value) / mid * 100)
        else:
            return int(-((value - mid) / mid) * 100)
