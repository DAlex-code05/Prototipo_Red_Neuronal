from flask import Flask, render_template, Response
import tensorflow as tf
import cv2
import numpy as np
from PIL import Image

app = Flask(__name__)

# Cargar el modelo previamente entrenado
model = tf.keras.models.load_model('modelo_mobilenet_v2.h5')

# Obtener los índices de clase
class_indices = {'perros': 0, 'gatos': 1, 'conejos': 2, 'pájaros': 3, 'hámsters': 4}
classes = list(class_indices.keys())

# Iniciar la captura de video
cap = cv2.VideoCapture(0)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)