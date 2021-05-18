from server.instance import server
import routes.facial as facial
import routes.finger as finger
from flask import jsonify
import RPi.GPIO as GPIO

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

# a simple page that says hello
@app.route('/hello')
def hello():
    return 'Hello, World!'

@app.route('/getFingerprint', methods=['GET'])
def getFingerprint():
    return 'Getting fingerprint...'

@app.route('/getFace', methods=['GET'])
def getFace():
    result = facial.takeFacePhoto(GREEN_LED, RED_LED)
    return jsonify(result)

if __name__ == '__main__':
    server.run()
    