from flask import Flask, render_template, Response, request, jsonify
import tensorflow as tf
import numpy as np
from PIL import Image
import base64
import io

app = Flask(__name__)

# Cargar el modelo
model_path = 'modelo_mobilenet_v2.h5'  # Cambia esto a la ruta de tu modelo
model = tf.keras.models.load_model(model_path)
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# Obtener los índices de clase
class_indices = {'perros': 0, 'gatos': 1, 'conejos': 2, 'pájaros': 3, 'hámsters': 4}
classes = list(class_indices.keys())

# Umbral de confianza para las predicciones
confidence_threshold = 0.7

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
    
    # Verificar que se haya proporcionado la imagen
    if 'image' not in data:
        return jsonify({'error': 'No se proporcionó la imagen'}), 400

    image_data = data['image']

    # Decodificar la imagen
    try:
        image_data = image_data.split(',')[1]  # Eliminar el prefijo "data:image/png;base64,"
        image = Image.open(io.BytesIO(base64.b64decode(image_data)))
    except Exception as e:
        return jsonify({'error': 'Error al procesar la imagen: ' + str(e)}), 400

    # Convertir la imagen a RGB si es necesario
    if image.mode != 'RGB':
        image = image.convert('RGB')

    # Preprocesar la imagen
    image = image.resize((224, 224))  # Cambia el tamaño según lo que necesite tu modelo
    img_array = np.array(image) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    # Realizar la predicción
    predictions = model.predict(img_array)
    predicted_class_index = np.argmax(predictions)
    confidence = predictions[0][predicted_class_index]  # Obtener la confianza de la predicción
    predicted_class = classes[predicted_class_index]

    # Verificar si la confianza es menor que el umbral
    if confidence < confidence_threshold:
        predicted_class = "animal no identificado"

    return jsonify({'class': predicted_class, 'confidence': float(confidence)})

if __name__ == '__main__':
    port = 5000
    app.run(host='127.0.0.1', port=port, debug=False)
