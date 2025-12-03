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
def stop_tank():
    left_track.stop()
    right_track.stop()
    print("Tank arrêté (sécurité).")


# === Heartbeat (sécurité si manette déconnectée) ===
last_event_time = time.time()
timeout = 1.0   # délai max sans événement


def heartbeat():
    global last_event_time
    while True:
        now = time.time()
        if now - last_event_time > timeout:
            print("⛔ Heartbeat timeout! Arrêt du tank.")
            stop_tank()
        time.sleep(0.2)


# === Boucle principale ===
def main():
    global last_event_time
    deadzone = 30
    xbox = XboxController("/dev/input/event4")
    xbox.start()

    while True:
        values = xbox.get_values()

        # Manette déconnectée
        if values is None:
            stop_tank()
            time.sleep(0.1)
            continue

        # Mise à jour du heartbeat UNIQUEMENT si nouvel événement
        if xbox.pop_new_event():
            last_event_time = time.time()

        # --- Chenille gauche (joystick gauche Y) ---
        raw_left = values.get("ABS_Y", 32767)
        val_gauche = xbox.convert_to_percent(raw_left)

        if abs(val_gauche) > deadzone:
            left_track.set_speed(val_gauche)
        else:
            left_track.stop()

        # --- Chenille droite (ABS_RZ) ---
        raw_right = values.get("ABS_RZ", 32767)
        val_droite = xbox.convert_to_percent(raw_right)

        if abs(val_droite) > deadzone:
            right_track.set_speed(val_droite)
        else:
            right_track.stop()

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
