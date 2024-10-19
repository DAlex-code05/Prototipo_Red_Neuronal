from flask import Flask, render_template, Response, request, jsonify
import tensorflow as tf
import cv2
import os
import numpy as np
from PIL import Image
import base64
import io

app = Flask(__name__)

# Cargar y compilar el modelo
model_path = os.getenv('MODEL_PATH')
if model_path is None:
    raise ValueError("La variable de entorno 'MODEL_PATH' no está definida. Asegúrate de establecerla correctamente.")
model = tf.keras.models.load_model(model_path)
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# Obtener los índices de clase
class_indices = {'perros': 0, 'gatos': 1, 'conejos': 2, 'pájaros': 3, 'hámsters': 4}
classes = list(class_indices.keys())

# Inicializar la captura de video
cap = cv2.VideoCapture(0)  # Asegúrate de que la cámara esté disponible

def gen_frames():
    while True:
        success, frame = cap.read()  # Lee el frame desde la cámara
        if not success:
            break
        else:
            # Preprocesar la imagen
            img = cv2.resize(frame, (224, 224))
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
            if not ret:
                break  # Si no se pudo codificar, salir del bucle

            # Yield el frame en el formato adecuado
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Ruta para la predicción
@app.route('/api/predict', methods=['POST'])
def predict():
    data = request.get_json()
    image_data = data['image']

    # Decodificar la imagen
    image_data = image_data.split(',')[1]  # Eliminar el prefijo "data:image/png;base64,"
    image = Image.open(io.BytesIO(base64.b64decode(image_data)))

    # Preprocesar la imagen
    image = image.resize((224, 224))  # Cambia el tamaño según lo que necesite tu modelo
    img_array = np.array(image) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    # Realizar la predicción
    predictions = model.predict(img_array)
    predicted_class_index = np.argmax(predictions)
    predicted_class = classes[predicted_class_index]

    return jsonify({'class': predicted_class})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)  # Usar la variable port
