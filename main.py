import RPi.GPIO as GPIO
import time
from evdev import InputDevice, categorize, ecodes

DEVICE_PATH = "/dev/input/event4"

# === Pins ===
forward_left = 20
rear_left = 21
forward_right = 19
rear_right = 26

vitesse_gauche = 16   # PWM GPIO
vitesse_droite = 13   # PWM GPIO
pwm_freq = 2000       # Hz

# === Config GPIO ===
GPIO.setmode(GPIO.BCM)

GPIO.setup(forward_left, GPIO.OUT)
GPIO.setup(rear_left, GPIO.OUT)
GPIO.setup(forward_right, GPIO.OUT)
GPIO.setup(rear_right, GPIO.OUT)

GPIO.setup(vitesse_gauche, GPIO.OUT)
GPIO.setup(vitesse_droite, GPIO.OUT)

# PWM
pwm_gauche = GPIO.PWM(vitesse_gauche, pwm_freq)
pwm_droite = GPIO.PWM(vitesse_droite, pwm_freq)
pwm_gauche.start(0)
pwm_droite.start(0)

# === Variables d’état ===
val_gauche = 0
val_droite = 0


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


def normalize(value):
    mid = 32767
    if value == mid:
        return 0

    if value < mid:
        return int((mid - value) / mid * 100)

    else:
        return int(-((value - mid) / mid) * 100)



def xbox_loop():
    global val_gauche, val_droite

    gamepad = InputDevice(DEVICE_PATH)

    for event in gamepad.read_loop():

        if event.type == ecodes.EV_SYN:
            continue

        if event.type == ecodes.EV_ABS:
            absevent = categorize(event)
            code = ecodes.ABS[absevent.event.code]
            value = absevent.event.value

            if code == "ABS_Y":
                val_gauche = normalize(value)

            elif code == "ABS_RZ":
                val_droite = normalize(value)

            # Appliquer en direct
            set_track_speed(val_gauche, forward_left, rear_left, pwm_gauche)
            set_track_speed(val_droite, forward_right, rear_right, pwm_droite)


try:
    print("Conduis le tank")
    xbox_loop()

finally:
    pwm_gauche.stop()
    pwm_droite.stop()
    GPIO.cleanup()
