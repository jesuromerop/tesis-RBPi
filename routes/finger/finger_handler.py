import time
import serial
import io
import RPi.GPIO as GPIO
import uuid

import adafruit_fingerprint

uart = serial.Serial("/dev/ttyUSB0", baudrate=57600, timeout=1)

finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)
    
def get_fingerprint():
    """Take a 2 finger images and template it, then store it in a file"""
    for fingerimg in range(1, 3):
        if fingerimg == 1:
            print("Place finger on sensor...", end="", flush=True)
        else:
            print("Place same finger again...", end="", flush=True)
        
        cont = 0

        while True:
            i = finger.get_image()
            if i == adafruit_fingerprint.OK:
                print("Image taken")
                break
            if i == adafruit_fingerprint.NOFINGER:
                print(".", end="", flush=True)
                time.sleep(0.01)
                cont += 1
                if cont >= 100:
                    print("Tiempo de espera agotado")
                    return {'success': False, 'mismatch': False, 'msg': "No se ha detectado la huella, intente nuevamente"}
            elif i == adafruit_fingerprint.IMAGEFAIL:
                print("Imaging error")
                return False
            else:
                print("Other error")
                return {'success': False, 'mismatch': False, 'msg': "Fallo al tomar la huella, intente nuevamente"}

        print("Templating...", end="", flush=True)
        i = finger.image_2_tz(fingerimg)
        if i == adafruit_fingerprint.OK:
            print("Templated")
        else:
            if i == adafruit_fingerprint.IMAGEMESS:
                print("Image too messy")
            elif i == adafruit_fingerprint.FEATUREFAIL:
                print("Could not identify features")
            elif i == adafruit_fingerprint.INVALIDIMAGE:
                print("Image invalid")
            else:
                print("Other error")
            return {'success': False, 'mismatch': False, 'msg': "Fallo al tomar la huella, intente nuevamente"}

        if fingerimg == 1:
            print("Remove finger")
            while i != adafruit_fingerprint.NOFINGER:
                i = finger.get_image()

    print("Creating model...", end="", flush=True)
    i = finger.create_model()
    if i == adafruit_fingerprint.OK:
        print("Created")
    else:
        if i == adafruit_fingerprint.ENROLLMISMATCH:
            print("Prints did not match")
            return {'success': False, 'mismatch': True, 'msg': "Las huellas ingresadas no coinciden, intente nuevamente"}
        else:
            print("Other error")
            return {'success': False, 'mismatch': False, 'msg': "Fallo al tomar la huella, intente nuevamente"}

    print("Downloading template...")
    data = finger.get_fpdata("char", 1)
    filename = f"{uuid.uuid4()}.dat"
    with open(f"./fingers/{filename}", "wb") as file:
        file.write(bytearray(data))
        print(f"Template is saved in {filename} file.")
    
    return {'success': True, 'msg': "Imagen tomada satisfactoriamente", 'data': filename}

