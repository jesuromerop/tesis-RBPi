import cv2
import face_recognition
from PIL import Image
import time
import RPi.GPIO as GPIO

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
        frame = video_capture.read()

        # Carga la imagen, la convierte a escala de grises y calcula el enfoque
        # usando el metodo de varianza de Laplace
        image = cv2.imread(frame)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        fm = variance_of_laplacian(gray)

        # Si la medida de enfoque es menor al umbral,
        # la imagen esta borrosa
        if fm < 100.0:
            GPIO.output(RED_LED, True)
            countBlurry +=1
            if countBlurry > 9:
                imgSuccess = False
        else:
            # Busca todas las caras del cuadro actual y las codifica
            face_locations = face_recognition.face_locations(frame)
            print("Found {} faces in image.".format(len(face_locations)))

            if len(face_locations) == 0:
                GPIO.output(RED_LED, True)
                countNoFace += 1
                if countBlurry > 9:
                    imgSuccess = False
            else:
                GPIO.output(RED_LED, False)
                # Imprime la ubicacion de todas las caras de la imagen
                top, right, bottom, left = face_locations
                print("A face is located at pixel location Top: {}, Left: {}, Bottom: {}, Right: {}".format(top, left, bottom, right))

                # Para acceder a la foto de la cara:
                face_image = image[top:bottom, left:right]
                pil_image = Image.fromarray(face_image)
                pil_image.show()
                imgSuccess = True
                break

        time.sleep(1)


    # Libera la camara
    video_capture.release()
    cv2.destroyAllWindows()

    if imgSuccess:
        return {'img': pil_image, 'success': True, 'msg': "Imagen tomada satisfactoriamente"}
    elif countBlurry > 9:
        return {'success': False, 'blurry': True, 'msg': "Fallo al tomar la imagen, foto borrosa"}
    else:
        return {'success': False, 'noFace': True, 'msg': "Fallo al tomar la imagen, no hay una cara en la foto"}