from flask import Flask, render_template, Response, request, jsonify
import tensorflow as tf
import numpy as np
from PIL import Image
import base64
import io
import os
import logging
import traceback
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
app = Flask(__name__)

MODEL_PATH = 'modelo_mobilenet_v2.h5'
IMAGE_SIZE = (224, 224)
CONFIDENCE_THRESHOLD = 0.7
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_IMAGE_SIZE = 10 * 1024 * 1024

try:
    model = tf.keras.models.load_model(MODEL_PATH)
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    logger.info("Modelo cargado exitosamente")
except Exception as e:
    logger.error(f"Error al cargar el modelo: {str(e)}")
    raise

class_indices = {'perros': 0, 'gatos': 1, 'conejos': 2, 'pájaros': 3, 'hámsters': 4}
classes = list(class_indices.keys())

def allowed_file_size(image_data):
    return len(image_data) <= MAX_IMAGE_SIZE

def preprocess_image(image):
    try:
        if image.mode != 'RGB':
            image = image.convert('RGB')
        image = image.resize(IMAGE_SIZE)
        img_array = np.array(image) / 255.0
        return np.expand_dims(img_array, axis=0)
    except Exception as e:
        logger.error(f"Error en el preprocesamiento de la imagen: {str(e)}")
        raise

def validate_image_data(image_data):
    if not image_data:
        raise ValueError("Datos de imagen vacíos")
    if not allowed_file_size(image_data):
        raise ValueError(f"Tamaño de imagen excede el límite de {MAX_IMAGE_SIZE/1024/1024}MB")

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error al cargar la página principal: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/predict', methods=['POST'])
def predict():
    start_time = datetime.now()
    logger.info("Iniciando nueva predicción")
    
    try:
        if not request.is_json:
            return jsonify({'error': 'Se requiere Content-Type: application/json'}), 400

        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({'error': 'No se proporcionó la imagen'}), 400

        image_data = data['image']

        try:
            image_data = image_data.split(',')[1]
            validate_image_data(image_data)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.error(f"Error al procesar datos base64: {str(e)}")
            return jsonify({'error': 'Formato de imagen inválido'}), 400

        try:
            image = Image.open(io.BytesIO(base64.b64decode(image_data)))
            processed_image = preprocess_image(image)
        except Exception as e:
            logger.error(f"Error al procesar la imagen: {str(e)}")
            return jsonify({'error': 'Error al procesar la imagen'}), 400

        try:
            predictions = model.predict(processed_image)
            predicted_class_index = np.argmax(predictions)
            confidence = float(predictions[0][predicted_class_index])
            predicted_class = classes[predicted_class_index] if confidence >= CONFIDENCE_THRESHOLD else "animal no identificado"
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"Predicción completada en {processing_time:.2f} segundos")
            return jsonify({
                'class': predicted_class,
                'confidence': confidence,
                'processing_time': processing_time
            })

        except Exception as e:
            logger.error(f"Error en la predicción: {str(e)}")
            return jsonify({'error': 'Error al realizar la predicción'}), 500

    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Recurso no encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f" Error interno del servidor: {str(error)}")
    return jsonify({'error': 'Error interno del servidor'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = bool(int(os.environ.get('FLASK_DEBUG', 0)))
    
    logger.info(f"Iniciando aplicación en puerto {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
