import RPi.GPIO as GPIO
import time

servo_pin = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(servo_pin, GPIO.OUT)

servo_pwm = GPIO.PWM(servo_pin, 50)  # 50 Hz PWM frequency
servo_pwm.start(0)  # Starting PWM signal with duty cycle of 0 (corresponds to 0 degrees)

#Go up
print("Going up")
for angle in range(90, -1, -1):
    duty_cycle = angle / 18.0 + 2.5
    servo_pwm.ChangeDutyCycle(duty_cycle)

time.sleep(5)

print("Going down")
for angle in range(0, 90):
    duty_cycle = angle / 18.0 + 2.5
    servo_pwm.ChangeDutyCycle(duty_cycle)
    time.sleep(0.05)  # Wait for 50ms before changing angle again



"""
try:
    while True:
        # Setting servo angle between 0 and 90 degrees
        print("Going down?")
        for angle in range(0, 90):
            duty_cycle = angle / 18.0 + 2.5
            servo_pwm.ChangeDutyCycle(duty_cycle)
            time.sleep(0.05)  # Wait for 50ms before changing angle again
        time.sleep(2)
        print("Down?")
        servo_pwm.ChangeDutyCycle(0)
        time.sleep(2)
        # Setting servo angle between 90 and 0 degrees
        print("Going up?")
        for angle in range(90, -1, -1):
            duty_cycle = angle / 18.0 + 2.5
            servo_pwm.ChangeDutyCycle(duty_cycle)
        time.sleep(2)
            

except KeyboardInterrupt:
    servo_pwm.stop()
    GPIO.cleanup()
"""