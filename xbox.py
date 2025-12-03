from evdev import InputDevice, categorize, ecodes
import threading
import time

class XboxController:
    def __init__(self, device_path="/dev/input/event4"):
        self.device_path = device_path
        self.gamepad = None
        self.connected = False

        # valeurs neutres (milieu des axes)
        self.neutral_values = {
            "ABS_Y": 32767,
            "ABS_RZ": 32767,
        }

        # valeurs courantes (initialisées au neutre)
        self.values = dict(self.neutral_values)

        # timestamp du dernier événement réellement reçu
        self.last_event = None

        self.running = False
        self.thread = None

    def _open_device(self):
        """Tente d'ouvrir le device. Retourne True si ok."""
        try:
            self.gamepad = InputDevice(self.device_path)
            self.connected = True
            print(f"[Xbox] Manette détectée : {self.device_path}")
            return True
        except Exception as e:
            self.connected = False
            # print(f"[Xbox] Impossible d'ouvrir {self.device_path}: {e}")
            return False

    def _read_loop(self):
        """Boucle de lecture continue. Met à jour last_event uniquement lorsque des events sont lus."""
        # tenter d'ouvrir le device une première fois
        if not self._open_device():
            print("[Xbox] Aucune manette trouvée, attente de connexion...")
            # tenter périodiquement d'ouvrir pendant que running est True
            while self.running and not self._open_device():
                time.sleep(1)
            if not self.running:
                return

        # si tout est OK on commence la lecture bloquante
        while self.running:
            try:
                # read_loop est bloquant et lève OSError si la manette est déconnectée
                for event in self.gamepad.read_loop():
                    if not self.running:
                        break

                    # Mettre à jour last_event quand on reçoit un event utile
                    now = time.time()
                    if event.type == ecodes.EV_ABS:
                        absevent = categorize(event)
                        code = ecodes.ABS[absevent.event.code]
                        value = absevent.event.value

                        # si on s'intéresse à ce code, on met à jour la valeur ET last_event
                        if code in self.values:
                            self.values[code] = value
                            self.last_event = now

                    elif event.type == ecodes.EV_KEY:
                        # si tu veux gérer des boutons, on peut aussi mettre à jour last_event
                        # keycode = event.code
                        self.last_event = now

                    # petite pause pour ne pas surcharger (pas nécessaire mais propre)
                    time.sleep(0.0005)

            except OSError:
                # normalement levé quand device est retiré/déconnecté
                print("[Xbox] Manette déconnectée (OSError).")
                self.connected = False
                # reset des valeurs à neutre
                self.values = dict(self.neutral_values)
                # marquer last_event à None pour signaler la déconnexion
                self.last_event = None

                # tenter reconnexion périodique tant que running = True
                while self.running and not self._open_device():
                    time.sleep(1)

                # si reconnecté, on continue la boucle and read_loop reprendra

            except Exception as e:
                # log d'erreur non bloquant
                print(f"[Xbox] Erreur inattendue dans read_loop: {e}")
                # on met en pause pour éviter boucle serrée en cas d'erreur continue
                time.sleep(0.5)

    def start(self):
        """Démarre le thread de lecture."""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._read_loop, daemon=True)
            self.thread.start()

    def stop(self):
        """Arrête la lecture."""
        self.running = False
        # on ne join pas le thread ici (daemon=True), mais tu peux le faire si tu veux attendre sa fin

    def get_values(self):
        """Retourne None si non connecté, sinon un dict copy des valeurs."""
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
