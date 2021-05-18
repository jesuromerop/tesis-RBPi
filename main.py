import time
import json 
import requests
import RPi.GPIO as GPIO
import cv2
import sys
import numpy as np
import face_recognition

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
    print(f"Status Code: {r.status_code}")
    if r.status_code != "200": 
        print(f"Cookie: {r.cookies['userToken']}")

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
    count = 1

    while True:
        # Obtiene un cuadro del video
        frame = video_capture.read()

        # Redimensiona el cuadro del video a 1/4 para procesamiento mas rapido
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convierte la imagen de color BGR (OpenCV) a RGB (face recognition)
        rgb_small_frame = small_frame[:, :, ::-1]

        # Busca todas las caras del cuadro actual y las codifica
        face_locations = face_recognition.face_locations(rgb_small_frame)
        print("Found {} faces in image.".format(len(face_locations)))

        if len(face_locations) == 0:
            GPIO.output(RED_LED, True)
        else:
            GPIO.output(RED_LED, False)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            matches = False
            for face_encoding in face_encodings:
                # Revisa si la cara del cuadro coincide con la cara conocida
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

            if matches[0]:
                print(matches)
                break
            else:
                print(matches)
                count += 1
                if count == 20:
                    break

    # Libera la camara
    video_capture.release()
    cv2.destroyAllWindows()

    return matches[0]

def blink_red_led():
    print("Blinking red led")
    GPIO.output(RED_LED, True)
    time.sleep(1)
    GPIO.output(RED_LED, False)
    time.sleep(1)
    GPIO.output(RED_LED, True)
    time.sleep(1)
    GPIO.output(RED_LED, False)
    time.sleep(1)
    GPIO.output(RED_LED, True)
    time.sleep(1)
    GPIO.output(RED_LED, False)
    time.sleep(1)

def blink_green_led():
    print("Blinking green led")
    GPIO.output(GREEN_LED, True)
    time.sleep(1)
    GPIO.output(GREEN_LED, False)
    time.sleep(1)
    GPIO.output(GREEN_LED, True)
    time.sleep(1)
    GPIO.output(GREEN_LED, False)
    time.sleep(1)
    GPIO.output(GREEN_LED, True)
    time.sleep(1)
    GPIO.output(GREEN_LED, False)
    time.sleep(1)

def get_face(url, cookies):
    req = s.get(f"{url}/getFace", cookies=dict(cookies))
    print(f"Status Code: {req.status_code}")
    print(f"Body: {req.text}")
    res_dict = req.json()
    print(res_dict['data'])
    r = s.get(f"{url}{res_dict['data']}")
    print(f"Status Code: {r.status_code}")

    return r.content

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
    b = True
    code = ""
    try:
        while b:
            for i in keypad:
                keypressed = readLine(i['line'], i['keys'])
                if "A" in keypressed:
                    keypressed = keypressed.strip("A")
                    code += keypressed
                    print(f"Key Pressed: {code}")
                    b = False
                    break
                else:
                    code += keypressed

            time.sleep(0.5)

        # Verificacion del codigo
        # body['code'] = code
        json_body = json.dumps(body)
        success = verify_code(url, headers, json_body)

        if success:
            blink_green_led()
            img = get_face(url, cookies)

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
            # raise Exception("codigo invalido")
            print("codigo invalido")
            blink_red_led()
    except KeyboardInterrupt:
            print("\nAplicacion detenida!")
            GPIO.cleanup()

if __name__ == "__main__":
    url = "http://192.168.1.239:3001"
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

    cookies = ""
    while True:
        main()
