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
varXbox = XboxController("/dev/input/event4")

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

def heartbeat(xbox_controller):
    global last_event_time
    while True:
        last_event = xbox_controller.last_event
        now = time.time()
        if now - last_event > timeout:
            print("Heartbeat timeout! Arrêt du tank.")
            stop_tank()
        print(now - last_event)
        time.sleep(0.2)


# === Boucle principale ===
def main():
    global last_event_time
    deadzone = 30
    varXbox.start()

    while True:
        values = varXbox.get_values()
        print(values)
        if values is None:
            time.sleep(0.02)
            continue
        last_event_time = time.time()
        # --- Chenille gauche (joystick gauche Y) ---
        if "ABS_Y" in values:
            raw = values["ABS_Y"]
            val_gauche = varXbox.convert_to_percent(raw)
            if val_gauche > deadzone or val_gauche < -deadzone:
                left_track.set_speed(val_gauche)
            else:
                left_track.stop()

        # --- Chenille droite (trigger / joystick selon ton mapping) ---
        if "ABS_RZ" in values:
            raw = values["ABS_RZ"]
            val_droite = varXbox.convert_to_percent(raw)
            if val_droite > deadzone or val_droite < -deadzone:
                right_track.set_speed(val_droite)
            else:
                right_track.stop()
        values = None
        time.sleep(0.02)


# === Programme principal ===
try:
    print("Conduis le tank!")
    threading.Thread(target=heartbeat, args=(varXbox,), daemon=True).start()
    main()

finally:
    stop_tank()
    left_track.cleanup()
    right_track.cleanup()
    GPIO.cleanup()