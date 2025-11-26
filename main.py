import RPi.GPIO as GPIO
import time
from evdev import InputDevice, categorize, ecodes
import threading
import xbox


DEVICE_PATH = "/dev/input/event4"

# === Pins ===
forward_left = 20
rear_left = 21
forward_right = 19
rear_right = 26

vitesse_gauche = 16
vitesse_droite = 13
pwm_freq = 2000

GPIO.setmode(GPIO.BCM)
GPIO.setup(forward_left, GPIO.OUT)
GPIO.setup(rear_left, GPIO.OUT)
GPIO.setup(forward_right, GPIO.OUT)
GPIO.setup(rear_right, GPIO.OUT)
GPIO.setup(vitesse_gauche, GPIO.OUT)
GPIO.setup(vitesse_droite, GPIO.OUT)

pwm_gauche = GPIO.PWM(vitesse_gauche, pwm_freq)
pwm_droite = GPIO.PWM(vitesse_droite, pwm_freq)
pwm_gauche.start(0)
pwm_droite.start(0)

# === Fonctions ===
def set_track_speed(percent, forward_pin, rear_pin, pwm):
    if percent > 0:
        GPIO.output(forward_pin, GPIO.HIGH)
        GPIO.output(rear_pin, GPIO.LOW)
        pwm.ChangeDutyCycle(percent)
    elif percent < 0:
        GPIO.output(forward_pin, GPIO.LOW)
        GPIO.output(rear_pin, GPIO.HIGH)
        pwm.ChangeDutyCycle(abs(percent))
    else:
        GPIO.output(forward_pin, GPIO.LOW)
        GPIO.output(rear_pin, GPIO.LOW)
        pwm.ChangeDutyCycle(0)

def stop_tank():
    set_track_speed(0, forward_left, rear_left, pwm_gauche)
    set_track_speed(0, forward_right, rear_right, pwm_droite)

def normalize(value):
    mid = 32767
    if value == mid:
        return 0
    if value < mid:
        return int((mid - value) / mid * 100)
    else:
        return int(-((value - mid) / mid) * 100)

# === Heartbeat ===
last_event_time = time.time()
timeout = 1.0  # secondes

def heartbeat():
    global last_event_time
    while True:
        now = time.time()
        if now - last_event_time > timeout:
            stop_tank()
        time.sleep(0.1)  # vérification toutes les 100 ms

# === Boucle manette ===
def main():
    while True:
        values = xbox.read_gamepad()
        # Exemple : utiliser ABS_Y pour vitesse gauche
        if "ABS_Y" in values:
            val_gauche = normalize(values["ABS_Y"])
            set_track_speed(val_gauche, forward_left, rear_left, pwm_gauche)
        if "ABS_RY" in values:
            val_droite = normalize(values["ABS_RY"])
            set_track_speed(val_droite, forward_right, rear_right, pwm_droite)

# === Main ===
try:
    print("Conduis le tank")
    threading.Thread(target=heartbeat, daemon=True).start()
finally:
    stop_tank()
    pwm_gauche.stop()
    pwm_droite.stop()
    GPIO.cleanup()