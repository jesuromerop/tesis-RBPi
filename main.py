import time
import json 
import requests
import RPi.GPIO as GPIO
from facial_recognition import facial_recognition

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
    print(f"Cookie: {r.cookies['userToken']}")

    return json.loads(r.content)['success']
    print(r.cookies)
    global cookies 
    cookies = r.cookies

def blink_red_led():
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
    r3 = s.get(f"{url}{res_dict['data']}")
    print(f"Status Code: {r3.status_code}")

    return r3.content

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

    except KeyboardInterrupt:
        print("\nAplicacion detenida!")

    # Verificacion del codigo
    body['code'] = code
    json_body = json.dumps(body)
    success = verify_code(url, headers, json_body)

    if success:
        img = get_face(url, cookies)

        with open("image.jpg", 'wb') as f:
            f.write(img)

        match = facial_recognition()
        if match:
            print("Reconocimiento facial exitoso")
            blink_green_led()
        else:
            print("Fallo el reconocimiento facial")
            blink_green_led()
    else: 
        # raise Exception("codigo invalido")
        print("codigo invalido")
        blink_red_led()

if __name__ == "__main__":
    url = "http://192.168.1.239:3001"
    headers = {'Content-Type': 'application/json'}
    body = {'pass': 123456, 'code': 156487}
    s = requests.Session() 

    # Puertos GPIO
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
    main()
