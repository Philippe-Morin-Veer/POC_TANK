import RPi.GPIO as GPIO

class Chenille:
    def __init__(self, forward_pin, rear_pin, pwm_pin, pwm_freq=2000):
        self.forward_pin = forward_pin
        self.rear_pin = rear_pin
        self.pwm_pin = pwm_pin

        GPIO.setup(self.forward_pin, GPIO.OUT)
        GPIO.setup(self.rear_pin, GPIO.OUT)
        GPIO.setup(self.pwm_pin, GPIO.OUT)

        self.pwm = GPIO.PWM(self.pwm_pin, pwm_freq)
        self.pwm.start(0)

    def set_speed(self, percent):
        """percent ∈ [-100, 100]"""

        if percent > 0:  # avancer
            GPIO.output(self.forward_pin, GPIO.HIGH)
            GPIO.output(self.rear_pin, GPIO.LOW)
            self.pwm.ChangeDutyCycle(percent)

        elif percent < 0:  # reculer
            GPIO.output(self.forward_pin, GPIO.LOW)
            GPIO.output(self.rear_pin, GPIO.HIGH)
            self.pwm.ChangeDutyCycle(abs(percent))

        else:  # stop
            GPIO.output(self.forward_pin, GPIO.LOW)
            GPIO.output(self.rear_pin, GPIO.LOW)
            self.pwm.ChangeDutyCycle(0)

    def forward(self, percent=100):
        self.set_speed(abs(percent))

    def backward(self, percent=100):
        self.set_speed(-abs(percent))

    def stop(self):
        self.set_speed(0)

    def cleanup(self):
        self.stop()
        self.pwm.stop()
