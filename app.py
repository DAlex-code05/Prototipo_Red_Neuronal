from flask import Flask, render_template, Response, request, jsonify
import tensorflow as tf
import os
import numpy as np
from PIL import Image
import base64
import io

app = Flask(__name__)

# Cargar y compilar el modelo
model_path = os.getenv('MODEL_PATH')
model = tf.keras.models.load_model(model_path)  # Corrección aquí
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# Obtener los índices de clase
class_indices = {'perros': 0, 'gatos': 1, 'conejos': 2, 'pájaros': 3, 'hámsters': 4}
classes = list(class_indices.keys())

@app.route('/')
def index():
    return render_template('index.html')

# Ruta para la predicción
@app.route('/api/predict', methods=['POST'])
def predict():
    try:
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
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)  # Usar la variable port
