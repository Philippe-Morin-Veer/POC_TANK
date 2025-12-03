import RPi.GPIO as GPIO
import time
import threading
from xbox import XboxController
from chenille import Chenille

forward_left = 20
rear_left = 21
forward_right = 19
rear_right = 26

vitesse_gauche = 16
vitesse_droite = 13
pwm_freq = 2000

varXbox = XboxController("/dev/input/event4")
isConnected = True

GPIO.setmode(GPIO.BCM)

left_track = Chenille(forward_left, rear_left, vitesse_gauche, pwm_freq)
right_track = Chenille(forward_right, rear_right, vitesse_droite, pwm_freq)

def stop_tank():
    left_track.stop()
    right_track.stop()
    print("Tank arrêté (sécurité).")

timeout = 2.0

def heartbeat(xbox_controller: XboxController):
    global isConnected
    print("Heartbeat started.")
    while True:
        now = time.time()

        if not xbox_controller.connected:
            if isConnected:
                print("Heartbeat: manette déconnectée.")
                stop_tank()
            isConnected = False
        else:
            delta = now - xbox_controller.last_event
            if delta > timeout:
                print(f"Heartbeat: aucun event depuis {delta:.2f}s.")
                stop_tank()
            isConnected = True

        time.sleep(0.2)

def main():
    deadzone = 30
    varXbox.start()

    while True:
        values = varXbox.get_values()

        if values is None:
            stop_tank()
            time.sleep(0.02)
            continue

        print(values)

        if "ABS_Y" in values and isConnected:
            raw = values["ABS_Y"]
            val_gauche = varXbox.convert_to_percent(raw)
            if val_gauche > deadzone or val_gauche < -deadzone:
                left_track.set_speed(val_gauche)
            else:
                left_track.stop()

        if "ABS_RZ" in values and isConnected:
            raw = values["ABS_RZ"]
            val_droite = varXbox.convert_to_percent(raw)
            if val_droite > deadzone or val_droite < -deadzone:
                right_track.set_speed(val_droite)
            else:
                right_track.stop()

        time.sleep(0.02)

try:
    print("Conduis")
    threading.Thread(target=heartbeat, args=(varXbox,), daemon=True).start()
    main()
finally:
    stop_tank()
    left_track.cleanup()
    right_track.cleanup()
    GPIO.cleanup()