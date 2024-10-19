from flask import Flask, render_template, Response
import tensorflow as tf
import cv2
import numpy as np
from PIL import Image
import os

app = Flask(__name__)

# Cargar el modelo previamente entrenado
model = tf.keras.models.load_model('modelo_mobilenet_v2.h5')

# Compilar el modelo (opcional, pero recomendado si se desea evitar advertencias)
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# Obtener los índices de clase
class_indices = {'perros': 0, 'gatos': 1, 'conejos': 2, 'pájaros': 3, 'hámsters': 4}
classes = list(class_indices.keys())

# Función para verificar cámaras disponibles
def check_cameras():
    available_cameras = []
    index = 0
    while True:
        cap = cv2.VideoCapture(index)
        if not cap.isOpened():
            break
        available_cameras.append(index)
        cap.release()
        index += 1
    return available_cameras

# Obtener el índice de cámara desde la variable de entorno
camera_index = int(os.environ.get('CAMERA_INDEX', 0))  # Valor por defecto 0

# Verificar si la cámara está disponible
cap = cv2.VideoCapture(camera_index)
if not cap.isOpened():
    raise Exception(f"No se pudo abrir la cámara en el índice {camera_index}.")

def gen_frames():
    while True:
        success, frame = cap.read()  # Lee el frame desde la cámara
        if not success:
            break
        else:
            # Preprocesar la imagen
            img = cv2.resize(frame, (224, 224))
            img = Image.fromarray(img)
            img_array = np.array(img) / 255.0
            img_array = np.expand_dims(img_array, axis=0)

            # Realizar la predicción
            predictions = model.predict(img_array)
            predicted_class_index = np.argmax(predictions)
            predicted_class = classes[predicted_class_index]

            # Mostrar el resultado en la imagen
            cv2.putText(frame, f'Predicción: {predicted_class}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Codificar el frame en JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = np.frombuffer(buffer, dtype=np.uint8)

            # Yield el frame en el formato adecuado
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame.tobytes() + b'\r\n')

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        return str(e), 500

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Nuevo endpoint para mostrar la variable PATH
@app.route('/path')
def show_path():
    path_value = os.environ.get('PATH', 'No se encontró la variable PATH')
    return f'El valor de PATH es: {path_value}'

if __name__ == '__main__':
    try:
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port)
    except Exception as e:
        print(f"Error al iniciar la aplicación: {e}")
