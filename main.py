from flask import Flask, render_template, Response, request
from picamera2 import Picamera2
from time import sleep
import cv2
from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero import AngularServo
import RPi.GPIO as gpio


app = Flask(__name__)

camera = Picamera2()
camera.configure(camera.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
camera.start()


# factory = PiGPIOFactory(host='192.168.20.16')
# run this command to get ip address in your mac or linux
# arp -a

from gpiozero import Servo
servo = Servo(12,
              min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
# Function to set the servo angle
def set_angle(angle):
    servo.value = angle
    sleep(1)

# motor code
def init():
    gpio.setmode(gpio.BCM)
    gpio.setup(17, gpio.OUT) # IN1
    gpio.setup(22, gpio.OUT) # IN2
    gpio.setup(23, gpio.OUT) # IN3
    gpio.setup(24, gpio.OUT) # IN4


def forward():
    init()
    gpio.output(17, True)
    gpio.output(22, False)
    gpio.output(23, True)
    gpio.output(24, False)
    sleep(1)
    gpio.cleanup()


def reverse():
    init()
    gpio.output(17, False)
    gpio.output(22, True)
    gpio.output(23, False)
    gpio.output(24, True)
    sleep(1)
    gpio.cleanup()


def right():
    init()
    gpio.output(17, True)
    gpio.output(22, False)
    gpio.output(23, False)
    gpio.output(24, True)
    sleep(1)
    gpio.cleanup()


def left():
    init()
    gpio.output(17, False)
    gpio.output(22, True)
    gpio.output(23, True)
    gpio.output(24, False)
    sleep(1)
    gpio.cleanup()

# from gpiozero import Servo
# Initialize the servo on GPIO pin 14
# min_pulse_width and max_pulse_width may need to be adjusted for your servo
# servo = AngularServo(14, min_angle=0, max_angle=180, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)


# camera related code
def generate_frames():
    while True:
        frame = camera.capture_array()
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/action', methods=['POST'])
def action():
    action = request.form.get('action')
    print(f"action {action}")

    if action == 'forward':
        forward()
        return action
    elif action == 'stop':
        # gpio.cleanup()
        return action
    elif action == 'backward':
        reverse()
        return action
    elif action == 'right':
        right()
        return action
    elif action == 'left':
        left()
        return action
    elif action == '10':
        set_angle(0)
        return action
    elif action == '90':
        set_angle(0.5)
        return action
    elif action == '180':
        set_angle(1)
        return action


    return "Invalid action"

if __name__ == '__main__':
    try:
        app.run(debug=False, host='0.0.0.0', threaded=True)
    except KeyboardInterrupt:
        pass
    finally:
        camera.release()
        gpio.cleanup()
