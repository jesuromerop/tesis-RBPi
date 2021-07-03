import time
import json 
import requests
import RPi.GPIO as GPIO
import cv2
import sys
import numpy as np
import face_recognition

keypadPressed = -1
code = ""

def readLine(line, characters):
    key = ""
    GPIO.output(line, GPIO.HIGH)

    if(GPIO.input(C1) == 1):
        key += characters[0]
        print(characters[0])

    if(GPIO.input(C2) == 1):
        key += characters[1]
        print(characters[1])

    if(GPIO.input(C3) == 1):
        key += characters[2]
        print(characters[2])

    if(GPIO.input(C4) == 1):
        key += characters[3]
        print(characters[3])

    GPIO.output(line, GPIO.LOW)
    return key

def verify_code(url, headers, json_body):
    r = s.get(f"{url}/verifyCode", headers=headers, data=json_body)
    if r.status_code == 200:
        print(f"Status Code: {r.status_code}")
        if json.loads(r.content)['success']: 
            print(f"Cookie: {r.cookies['userToken']}")
        else:
            print(f"Codigo invalido!")
            blink_red_led()
    else:
        print(f"Error {r.status_code}")

    return json.loads(r.content)['success']

def facial_recognition():
    # Obtiene imagen de la camara 0
    video_capture = cv2.VideoCapture(0)

    # Carga una imagen y aprende a reconocerla
    image = face_recognition.load_image_file("image.jpg")
    face_encoding = face_recognition.face_encodings(image)[0]

    # Arreglo de caras conocidas
    known_face_encodings = [
        face_encoding
    ]

    # Inicializacion de variables
    face_locations = []
    face_encodings = []
    count = 0

    while True:
        # Obtiene un cuadro del video
        ret, frame = video_capture.read()

        # Redimensiona el cuadro del video a 1/4 para procesamiento mas rapido
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convierte la imagen de color BGR (OpenCV) a RGB (face recognition)
        rgb_small_frame = small_frame[:, :, ::-1]

        # Busca todas las caras del cuadro actual y las codifica
        face_locations = face_recognition.face_locations(rgb_small_frame)
        print("Found {} faces in image.".format(len(face_locations)))
        matches = False

        if len(face_locations) == 0:
            GPIO.output(RED_LED, True)
            time.sleep(0.01)
            count += 1
            if count == 100:
                break
        else:
            GPIO.output(RED_LED, False)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            for face_encoding in face_encodings:
                # Revisa si la cara del cuadro coincide con la cara conocida
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)[0]

            if matches:
                print(matches)
                break
            else:
                print(matches)
                time.sleep(0.01)
                count += 1
                if count == 100:
                    break

    # Libera la camara
    video_capture.release()
    cv2.destroyAllWindows()

    return matches

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

def get_face(url):
    req = s.get(f"{url}/getFace")
    if req.status_code == 200:
        print(f"Status Code: {req.status_code}")
        print(f"Body: {req.text}")
        res_dict = req.json()
        print(res_dict['data'])
        if res_dict['data']:
            r = s.get(f"{url}{res_dict['data']}")
            print(f"Status Code: {r.status_code}")
        else:
            return False
    else:
        raise(f"Error {req.status_code}")

    return r.content

def get_fingers(url):
    req = s.get(f"{url}/getFinger")
    if req.status_code == 200:
        print(f"Status Code: {req.status_code}")
        print(f"Body: {req.text}")
        res_dict = req.json()
        print(res_dict['data'])
        if res_dict['data']:
            finger_img = []
            for fingerprint in res_dict['data']:
                finger_img.append({"fingerName": fingerprint['fingerName'], "data": fingerprint['data']})
        else:
            return False
    else:
        raise(f"Error {req.status_code}")

    return finger_img

def match_fingerprint(fingers):
    import serial
    import adafruit_fingerprint

    uart = serial.Serial("/dev/ttyUSB1", baudrate=57600, timeout=1)
    finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)

    """Compares a new fingerprint template to an existing template stored in a file
    This is useful when templates are stored centrally (i.e. in a database)"""
    
    print("Waiting for finger print...")
    cont = 0
    while finger.get_image() != adafruit_fingerprint.OK:
        print("Dedo no detectado")
        time.sleep(0.01)
        cont += 1
        if cont >= 100:
            print("Tiempo de espera agotado")
            return False

    print("Templating...")
    if finger.image_2_tz(1) != adafruit_fingerprint.OK:
        return False

    print(fingers)
    for f in fingers:
        print("Loading file template...")
        with open(f"./fingers/{f['data']}", "rb") as file:
            data = file.read()
        #print(list(data))
        finger.send_fpdata(list(data), "char", 2)
        finger.image_2_tz(2)
        finger.create_model()
        i = finger.compare_templates()
        if i == adafruit_fingerprint.OK:
            # set_led_local(color=2, speed=150, mode=6)
            print(f"La huella coincide con la huella de la base de datos {f['fingerName']}")
            return True
        if i == adafruit_fingerprint.NOMATCH:
            # set_led_local(color=1, mode=2, speed=20, cycles=10)
            print(f"Las huellas no coinciden! {f['fingerName']}")
        else:
            print("Other error!")
       # finger.set_fpdata(data_finger1, "char", 1)
    return False

def create_record():
    req = s.post(f"{url}/setRecord", cookies=dict(cookies))
    print(f"Status Code: {req.status_code}")
    print(f"Body: {req.text}")
    res_dict = req.json()
    print(res_dict['msg'])

    if res_dict['success']:
        return True
    else:
        return False

def main():
    #b = True
    #cont = 0
    global code
    global keypadPressed
    # try:
    #     while b:
    #         for i in keypad:
    #             keypressed = readLine(i['line'], i['keys'])
    #             if "A" in keypressed:
    #                 keypressed = keypressed.strip("A")
    #                 code += keypressed
    #                 print(f"Key Pressed: {code}")
    #                 b = False
    #                 break
    #             else:
    #                 if code != "":
    #                     if code[-1] != keypressed:
    #                         code += keypressed
    #                         cont = 0
    #                     else:
    #                         cont += 1
    #                         if cont >= 18:
    #                             code += keypressed
    #                             cont = 0
    #                 else:
    #                     code += keypressed

    #         time.sleep(0.115)
    try:
        print("Ingrese el codigo")
        while True:
            # If a button was previously pressed,
            # check, whether the user has released it yet
            if keypadPressed != -1:
                setAllLines(GPIO.HIGH)
                if GPIO.input(keypadPressed) == 0:
                    keypadPressed = -1
                else:
                    time.sleep(0.1)
            # Otherwise, just read the input
            else:
                result = checkSpecialKeys()
                if not result['pressedA'] and not result['pressedC']:
                    readLine(L1, ["1","2","3","A"])
                    readLine(L2, ["4","5","6","B"])
                    readLine(L3, ["7","8","9","C"])
                    readLine(L4, ["*","0","#","D"])
                    time.sleep(0.1)
                else:
                    if result['pressedA']:
                        break
                    else:
                        time.sleep(0.1)

        # Verificacion del codigo
        body['code'] = code
        json_body = json.dumps(body)
        success = verify_code(url, headers, json_body)
        code = ""
        if success:
            blink_green_led()
            
            fingers = get_fingers(url)
            # print(fingers)

            if fingers:
                match_finger = match_fingerprint(fingers)
            else:
                match_finger = True
            
            if match_finger: 
                img = get_face(url)

                if img:
                    with open("image.jpg", 'wb') as f:
                        f.write(img)

                    match = facial_recognition()
                    if match:
                        print("Reconocimiento facial exitoso")
                        blink_green_led()
                        record = create_record()
                        if record:
                            print("Registro creado satisfactoriamente")
                        else:
                            print("Error al crear registro")
                    else:
                        print("Fallo el reconocimiento facial")
                        blink_red_led()
                else:
                    record = create_record()
                    if record:
                        print("Registro creado satisfactoriamente")
                    else:
                        print("Error al crear registro")
        else: 
            # raise Exception("codigo invalido")
            print("Ha ocurrido un error")
            blink_red_led()
    except KeyboardInterrupt:
            print("\nAplicacion detenida!")
            GPIO.cleanup()
            
# This callback registers the key that was pressed
# if no other key is currently pressed
def keypadCallback(channel):
    global keypadPressed
    if keypadPressed == -1:
        keypadPressed = channel

# Sets all lines to a specific state. This is a helper
# for detecting when the user releases a button
def setAllLines(state):
    GPIO.output(L1, state)
    GPIO.output(L2, state)
    GPIO.output(L3, state)
    GPIO.output(L4, state)

def checkSpecialKeys():
    global code
    pressedC = False
    pressedA = False

    GPIO.output(L2, GPIO.HIGH)

    if (GPIO.input(C4) == 1):
        print("Reset del codigo!")
        pressedC = True

    GPIO.output(L2, GPIO.LOW)
    GPIO.output(L1, GPIO.HIGH)

    if (not pressedC and GPIO.input(C4) == 1):
        pressedA = True

    GPIO.output(L3, GPIO.LOW)

    if pressedC:
        code = ""

    return { "pressedA": pressedA, "pressedC": pressedC }

# reads the columns and appends the value, that corresponds
# to the button, to a variable
def readLine(line, characters):
    global code
    # We have to send a pulse on each line to
    # detect button presses
    GPIO.output(line, GPIO.HIGH)
    if(GPIO.input(C1) == 1):
        code = code + characters[0]
        print(code)
    if(GPIO.input(C2) == 1):
        code = code + characters[1]
        print(code)
    if(GPIO.input(C3) == 1):
        code = code + characters[2]
        print(code)
    if(GPIO.input(C4) == 1):
        code = code + characters[3]
        print(code)
    GPIO.output(line, GPIO.LOW)

if __name__ == "__main__":
    #url = "http://192.168.1.239:3001"
    url = "http://172.28.168.204:3001"
    headers = {'Content-Type': 'application/json'}
    body = {'pass': 123456, 'code': 156487}
    s = requests.Session() 

    # Puertos GPIO
    # Pinout:
    # 1: Not Used
    # 2-5: Columns 1-4
    # 6-9: Rows 1-4
    # 10: Not used
    L1 = 12
    L2 = 16
    L3 = 20
    L4 = 21

    C1 = 5
    C2 = 6
    C3 = 13
    C4 = 19

    GREEN_LED = 23
    RED_LED = 24

    keypad = [
        {'line': L1, 'keys': ["1","2","3","A"]}, 
        {'line': L2, 'keys': ["4","5","6","B"]}, 
        {'line': L3, 'keys': ["7","8","9","C"]}, 
        {'line': L4, 'keys': ["*","0","#","D"]}
    ]   
    columns = [C1, C2, C3, C4]

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    # Configuracion de puertos de salida para los leds
    # LED verde
    GPIO.setup(GREEN_LED, GPIO.OUT)
    # LED rojo
    GPIO.setup(RED_LED, GPIO.OUT)

    # Configuracion de puertos de salida para el keypad
    for i in keypad:
            GPIO.setup(i['line'], GPIO.OUT)

    for i in columns:
            GPIO.setup(i, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    # Detect the rising edges on the column lines of the
    # keypad. This way, we can detect if the user presses
    # a button when we send a pulse.
    GPIO.add_event_detect(C1, GPIO.RISING, callback=keypadCallback)
    GPIO.add_event_detect(C2, GPIO.RISING, callback=keypadCallback)
    GPIO.add_event_detect(C3, GPIO.RISING, callback=keypadCallback)
    GPIO.add_event_detect(C4, GPIO.RISING, callback=keypadCallback)

    cookies = ""
    while True:
        main()
