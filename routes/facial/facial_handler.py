import cv2
import face_recognition
from PIL import Image
import time
import io
from base64 import encodebytes
import RPi.GPIO as GPIO

def get_response_image(image):
    byte_arr = io.BytesIO()
    image.save(byte_arr, format='PNG') # convert the PIL image to byte array
    encoded_img = encodebytes(byte_arr.getvalue()).decode('ascii') # encode as base64
    return encoded_img

def variance_of_laplacian(image):
	# Calcula el Laplace de la imagen y devuelve la medida de enfoque
	# el cual es la varianza de Laplace
	return cv2.Laplacian(image, cv2.CV_64F).var()

def takeFacePhoto(GREEN_LED, RED_LED):
    # Obtiene imagen de la camara 0
    video_capture = cv2.VideoCapture(0)

    countBlurry = 0
    countNoFace = 0

    while True:
        # Obtiene un cuadro del video
        ret, frame = video_capture.read()
        
        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        
        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]
        
        # Busca todas las caras del cuadro actual y las codifica
        face_locations = face_recognition.face_locations(rgb_small_frame)
        print("Found {} faces in image.".format(len(face_locations)))

        if len(face_locations) == 0:
            print("No face")
            GPIO.output(RED_LED, True)
            countNoFace += 1
            if countNoFace > 9:
                imgSuccess = False
                break
        else:
            # Carga la imagen, la convierte a escala de grises y calcula el enfoque
            # usando el metodo de varianza de Laplace
            image = frame
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            fm = variance_of_laplacian(gray)

            # Si la medida de enfoque es menor al umbral,
            # la imagen esta borrosa
            print(f"Focus mesurement {fm}")
            if fm < 20.0:
                GPIO.output(RED_LED, True)
                print("Blurry face")
                countBlurry +=1
                if countBlurry > 9:
                    imgSuccess = False
                    break
            else:
                GPIO.output(RED_LED, False)
                print("Got clear face")
                # Imprime la ubicacion de todas las caras de la imagen
                top, right, bottom, left = face_locations[0]
                print("A face is located at pixel location Top: {}, Left: {}, Bottom: {}, Right: {}".format(top, left, bottom, right))

                top *= 3#6
                right *= 6#5
                bottom *= 6#2
                left *= 2#3
                
                # Para acceder a la foto de la cara:
                face_image = frame[top:bottom, left:right, ::-1]#[:, :, ::-1] #
                pil_image = Image.fromarray(face_image)
                #pil_image.show()
                pil_image.save("tempface.jpg")
                
                encoded_img = get_response_image(pil_image)
                
                imgSuccess = True
                break
        
            

        time.sleep(1)


    # Libera la camara
    video_capture.release()
    cv2.destroyAllWindows()
    GPIO.output(RED_LED, False)
    if imgSuccess:
        return {'base64_img': encoded_img, 'success': True, 'msg': "Imagen tomada satisfactoriamente"}
    elif countBlurry > 9:
        return {'success': False, 'blurry': True, 'msg': "Fallo al tomar la imagen, foto borrosa"}
    else:
        return {'success': False, 'noFace': True, 'msg': "Fallo al tomar la imagen, no hay una cara en la foto"}