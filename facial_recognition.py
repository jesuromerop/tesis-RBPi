import cv2
import numpy as np
import face_recognition
import RPi.GPIO as GPIO

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
    face_names = []
    process_this_frame = True
    count = 1

    while True:
        # Obtiene un cuadro del video
        ret, frame = video_capture.read()

        # Redimensiona el cuadro del video a 1/4 para procesamiento mas rapido
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convierte la imagen de color BGR (OpenCV) a RGB (face recognition)
        rgb_small_frame = small_frame[:, :, ::-1]

        # Only process every other frame of video to save time
        if process_this_frame:
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

                if matches:
                    print(matches)
                    process_this_frame = not process_this_frame
                else:
                    print(matches)
                    count += 1
                    if count == 20:
                        process_this_frame = not process_this_frame

    # Libera la camara
    video_capture.release()
    cv2.destroyAllWindows()

    return matches