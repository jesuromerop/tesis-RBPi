import time
import serial
import io
# from base64 import encodebytes
import RPi.GPIO as GPIO
import uuid

import adafruit_fingerprint

uart = serial.Serial("/dev/ttyUSB1", baudrate=57600, timeout=1)

finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)

# def get_response_image(image):
#     byte_arr = io.BytesIO()
#     image.save(byte_arr, format='PNG') # convert the PIL image to byte array
#     #return encodebytes(byte_arr.getvalue()).decode('ascii') # encode as base64

# def save_fingerprint_image(result):
#     # let PIL take care of the image headers and file structure
#     from PIL import Image  # pylint: disable=import-outside-toplevel

#     img = Image.new("L", (256, 288), "white")
#     pixeldata = img.load()
#     mask = 0b00001111
#     # result = finger.get_fpdata(sensorbuffer="image")

#     # this block "unpacks" the data received from the fingerprint
#     #   module then copies the image data to the image placeholder "img"
#     #   pixel by pixel.  please refer to section 4.2.1 of the manual for
#     #   more details.  thanks to Bastian Raschke and Danylo Esterman.
#     # pylint: disable=invalid-name
#     x = 0
#     # pylint: disable=invalid-name
#     y = 0
#     # pylint: disable=consider-using-enumerate
#     for i in range(len(result)):
#         pixeldata[x, y] = (int(result[i]) >> 4) * 17
#         x += 1
#         pixeldata[x, y] = (int(result[i]) & mask) * 17
#         if x == 255:
#             x = 0
#             y += 1
#         else:
#             x += 1

#     if not img.save("tempfinger.png"):
#         return get_response_image(img)
#     return False
    
def get_fingerprint():
    """Take a 2 finger images and template it, then store it in a file"""
    #set_led_local(color=3, mode=1)
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
                #set_led_local(color=1, mode=2, speed=20, cycles=10)
                print("Imaging error")
                return False
            else:
                #set_led_local(color=1, mode=2, speed=20, cycles=10)
                print("Other error")
                return {'success': False, 'mismatch': False, 'msg': "Fallo al tomar la huella, intente nuevamente"}

        print("Templating...", end="", flush=True)
        i = finger.image_2_tz(fingerimg)
        if i == adafruit_fingerprint.OK:
            print("Templated")
        else:
            if i == adafruit_fingerprint.IMAGEMESS:
                #set_led_local(color=1, mode=2, speed=20, cycles=10)
                print("Image too messy")
            elif i == adafruit_fingerprint.FEATUREFAIL:
                #set_led_local(color=1, mode=2, speed=20, cycles=10)
                print("Could not identify features")
            elif i == adafruit_fingerprint.INVALIDIMAGE:
                #set_led_local(color=1, mode=2, speed=20, cycles=10)
                print("Image invalid")
            else:
                #set_led_local(color=1, mode=2, speed=20, cycles=10)
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
            #set_led_local(color=1, mode=2, speed=20, cycles=10)
            print("Prints did not match")
            return {'success': False, 'mismatch': True, 'msg': "Las huellas ingresadas no coinciden, intente nuevamente"}
        else:
            #set_led_local(color=1, mode=2, speed=20, cycles=10)
            print("Other error")
            return {'success': False, 'mismatch': False, 'msg': "Fallo al tomar la huella, intente nuevamente"}

    print("Downloading template...")
    data = finger.get_fpdata("char", 1)
    filename = f"{uuid.uuid4()}.dat"
    with open(f"./fingers/{filename}", "wb") as file:
        file.write(bytearray(data))
        print(f"Template is saved in {filename} file.")
    
    return {'success': True, 'msg': "Imagen tomada satisfactoriamente", 'data': filename}
    #set_led_local(color=2, speed=150, mode=6)

# def get_fingerprint2(blink_green_led, blink_red_led, location):
#     """Take a 2 finger images and template it, then store in 'location'"""
#     timeoutCount = 0
#     for fingerimg in range(1, 3):
#         if fingerimg == 1:
#             print("Place finger on sensor...", end="", flush=True)
#         else:
#             print("Place same finger again...", end="", flush=True)

#         while True:
#             i = finger.get_image()
#             if i == adafruit_fingerprint.OK:
#                 print("Image taken")
#                 if fingerimg == 2:
#                     result = finger.get_fpdata(sensorbuffer="image")

#                 break
#             if i == adafruit_fingerprint.NOFINGER:
#                 timeoutCount += 1
#                 if timeoutCount == 30:
#                     return {'success': False, 'mismatch': False, 'msg': "No se ha detectado ninguna huella, intente nuevamente"}
#                 print(".", end="", flush=True)
#             elif i == adafruit_fingerprint.IMAGEFAIL:
#                 return _fingerprint_return_msg(
#                     "Imaging error",
#                     blink_red_led,
#                     False,
#                     "Fallo al tomar la huella, intente nuevamente",
#                 )

#             else:
#                 return _fingerprint_return_msg(
#                     "Other error",
#                     blink_red_led,
#                     False,
#                     "Fallo al tomar la huella, intente nuevamente",
#                 )

#         print("Templating...", end="", flush=True)
#         i = finger.image_2_tz(fingerimg)
#         if i == adafruit_fingerprint.OK:
#             print("Templated")
#         else:
#             if i == adafruit_fingerprint.IMAGEMESS:
#                 print("Image too messy")
#             elif i == adafruit_fingerprint.FEATUREFAIL:
#                 print("Could not identify features")
#             elif i == adafruit_fingerprint.INVALIDIMAGE:
#                 print("Image invalid")
#             else:
#                 print("Other error")
#             blink_red_led()
#             return {'success': False, 'mismatch': False, 'msg': "Fallo al tomar la huella, intente nuevamente"}

#         if fingerimg == 1:
#             print("Remove finger")
#             time.sleep(1)
#             while i != adafruit_fingerprint.NOFINGER:
#                 i = finger.get_image()

#         time.sleep(1)        

#     print("Creating model...", end="", flush=True)
#     i = finger.create_model()
#     if i == adafruit_fingerprint.OK:
#         print("Created")
#     else:
#         if i == adafruit_fingerprint.ENROLLMISMATCH:
#             return _fingerprint_return_msg(
#                 "Prints did not match",
#                 blink_red_led,
#                 True,
#                 "Las huellas ingresadas no coinciden, intente nuevamente",
#             )

#         else:
#             print("Other error")
#         blink_red_led()
#         return {'success': False, 'mismatch': False, 'msg': "Fallo al tomar la huella, intente nuevamente"}

#     print("Storing model #%d..." % location, end="", flush=True)
#     i = finger.store_model(location)
#     if i == adafruit_fingerprint.OK:
#         print("Stored")
#         encoded_img = save_fingerprint_image(result)

#         if not encoded_img:
#             return {'success': False, 'mismatch': False, 'msg': "Fallo al tomar la huella, intente nuevamente"}

#         blink_green_led()
#         return {'base64_img': encoded_img, 'success': True, 'msg': "Imagen tomada satisfactoriamente"}
#     else:
#         if i == adafruit_fingerprint.BADLOCATION:
#             print("Bad storage location")
#         elif i == adafruit_fingerprint.FLASHERR:
#             print("Flash storage error")
#         else:
#             print("Other error")
#         blink_red_led()
#         return {'success': False, 'mismatch': False, 'msg': "Fallo al tomar la huella, intente nuevamente"}
