import RPi.GPIO as GPIO
import time
import threading
from xbox import XboxController
from chenille import Chenille

# === Pins ===
forward_left = 20
rear_left = 21
forward_right = 19
rear_right = 26

vitesse_gauche = 16
vitesse_droite = 13
pwm_freq = 2000

GPIO.setmode(GPIO.BCM)

# === Création des deux chenilles ===
left_track = Chenille(forward_left, rear_left, vitesse_gauche, pwm_freq)
right_track = Chenille(forward_right, rear_right, vitesse_droite, pwm_freq)


# === Fonctions ===
"""def normalize(value):
    mid = 32767
    if value == mid:
        return 0
    if value < mid:
        return int((mid - value) / mid * 100)
    else:
        return int(-((value - mid) / mid) * 100)"""


def stop_tank():
    left_track.stop()
    right_track.stop()
    print("Tank arrêté (sécurité).")


# === Heartbeat (sécurité si manette déconnectée) ===
last_event_time = time.time()
timeout = 1.0

def heartbeat():
    global last_event_time
    while True:
        now = time.time()
        if now - last_event_time > timeout:
            stop_tank()
        time.sleep(0.1)


# === Boucle principale ===
def main():
    global last_event_time

    xbox = XboxController("/dev/input/event4")
    xbox.start()

    while True:
        values = xbox.get_values()
        if values is None:
            time.sleep(0.02)
            continue
        last_event_time = time.time()

        # --- Chenille gauche (joystick gauche Y) ---
        if "ABS_Y" in values:
            raw = values["ABS_Y"]
            val_gauche = xbox.convert_to_percent(raw)
            if val_gauche > 30 or val_gauche < -30:
                left_track.set_speed(val_gauche)

        # --- Chenille droite (trigger / joystick selon ton mapping) ---
        if "ABS_RZ" in values:
            raw = values["ABS_RZ"]
            val_droite = xbox.convert_to_percent(raw)
            if val_droite > 30 or val_droite < -30:
                right_track.set_speed(val_droite)

        time.sleep(0.02)


# === Programme principal ===
try:
    print("Conduis le tank!")
    threading.Thread(target=heartbeat, daemon=True).start()
    main()

finally:
    stop_tank()
    left_track.cleanup()
    right_track.cleanup()
    GPIO.cleanup()