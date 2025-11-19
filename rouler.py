import RPi.GPIO as GPIO
import time

# === Pins ===
forward_left = 20
rear_left = 21
forward_right = 19
rear_right = 26

vitesse_gauche = 16   # PWM
vitesse_droite = 13   # PWM
pwm_freq = 2000       # Fréquence PWM

# === Configuration des GPIO ===
GPIO.setmode(GPIO.BCM)

GPIO.setup(forward_left, GPIO.OUT)
GPIO.setup(rear_left, GPIO.OUT)
GPIO.setup(forward_right, GPIO.OUT)
GPIO.setup(rear_right, GPIO.OUT)

GPIO.setup(vitesse_gauche, GPIO.OUT)
GPIO.setup(vitesse_droite, GPIO.OUT)

# === PWM ===
pwm_gauche = GPIO.PWM(vitesse_gauche, pwm_freq)
pwm_droite = GPIO.PWM(vitesse_droite, pwm_freq)

pwm_gauche.start(0)   # duty cycle à 0%
pwm_droite.start(0)

try:
    # === Avancer ===
    print("Tank avance pendant 2 secondes...")

    # Direction : avant = forward = HIGH, rear = LOW
    GPIO.output(forward_left, GPIO.HIGH)
    GPIO.output(rear_left, GPIO.LOW)
    GPIO.output(forward_right, GPIO.HIGH)
    GPIO.output(rear_right, GPIO.LOW)

    # Vitesse (duty cycle 0 à 100)
    pwm_gauche.ChangeDutyCycle(80)   # 80% (tu peux ajuster)
    pwm_droite.ChangeDutyCycle(80)

    time.sleep(2)

    print("Stop.")

    # === Stop ===
    GPIO.output(forward_left, GPIO.LOW)
    GPIO.output(rear_left, GPIO.LOW)
    GPIO.output(forward_right, GPIO.LOW)
    GPIO.output(rear_right, GPIO.LOW)
    pwm_gauche.ChangeDutyCycle(0)
    pwm_droite.ChangeDutyCycle(0)

finally:
    pwm_gauche.stop()
    pwm_droite.stop()
    GPIO.cleanup()
