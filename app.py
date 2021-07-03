from flask.helpers import make_response
from server.instance import server
import routes.facial as facial
import routes.finger as finger
from flask import jsonify, send_file
import RPi.GPIO as GPIO
from flask_cors import CORS
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GREEN_LED = 23
RED_LED = 24
# Configuracion de puertos de salida para los leds
# LED verde
GPIO.setup(GREEN_LED, GPIO.OUT)
# LED rojo
GPIO.setup(RED_LED, GPIO.OUT)

app = server.app
CORS(app)


def blink_red_led():
    print("Blinking red led")
    GPIO.output(RED_LED, True)
    time.sleep(0.4)
    GPIO.output(RED_LED, False)
    time.sleep(0.4)
    GPIO.output(RED_LED, True)
    time.sleep(0.4)
    GPIO.output(RED_LED, False)
    time.sleep(0.4)
    GPIO.output(RED_LED, True)
    time.sleep(0.4)
    GPIO.output(RED_LED, False)
    time.sleep(0.4)

def blink_green_led():
    print("Blinking green led")
    GPIO.output(GREEN_LED, True)
    time.sleep(0.4)
    GPIO.output(GREEN_LED, False)
    time.sleep(0.4)
    GPIO.output(GREEN_LED, True)
    time.sleep(0.4)
    GPIO.output(GREEN_LED, False)
    time.sleep(0.4)
    GPIO.output(GREEN_LED, True)
    time.sleep(0.4)
    GPIO.output(GREEN_LED, False)
    time.sleep(0.4)

# a simple page that says hello
@app.route('/hello')
def hello():
    return 'Hello, World!'

@app.route('/getFingerprint', methods=['GET'])
def getFingerprint():
    print('Getting fingerprint...')
    #result = finger.get_fingerprint(blink_green_led, blink_red_led, 0)
    result = finger.get_fingerprint()
    return jsonify(result)

@app.route('/getFace', methods=['GET'])
def getFace():
    result = facial.takeFacePhoto(GREEN_LED, RED_LED)
    return jsonify(result)

if __name__ == '__main__':
    server.run()
    