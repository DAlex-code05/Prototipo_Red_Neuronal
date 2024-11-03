/**
 * main.js - Funcionalidad principal para la aplicación de clasificación de imágenes
 * Este script maneja la captura de imágenes, la interacción con la API de predicción, el almacenamiento en caché de predicciones, y la gestión del historial de predicciones. También incluye manejo de errores y logging para facilitar la depuración.
 */

/**
 * Calcula un hash simple para una cadena de datos de imagen.
 * @param {string} imageData - Datos de la imagen en formato base64.
 * @returns {number} Un valor hash numérico.
 */
function simpleHash(imageData) {
    // ... (código de la función)
}

/**
 * Carga y muestra el historial de predicciones guardado en localStorage.
 * Muestra las últimas 10 predicciones en orden inverso cronológico.
 */
function loadHistory() {
    // ... (código de la función)
}

/**
 * Guarda una nueva predicción en el historial.
 * Mantiene solo las últimas 10 predicciones.
 * @param {Object} prediction - Objeto con los datos de la predicción.
 */
function savePrediction(prediction) {
    // ... (código de la función)
}

/**
 * Limpia la caché de predicciones almacenada en localStorage.
 * Mantiene intacto el historial de predicciones.
 */
function clearPredictionCache() {
    // ... (código de la función)
}

/**
 * Captura una imagen de la cámara web y realiza una predicción.
 * Utiliza caché local para predicciones previas de la misma imagen.
 */
function captureAndPredict() {
    // ... (código de la función)
}

// Inicialización cuando el DOM está completamente cargado
document.addEventListener('DOMContentLoaded', function() {
    /**
     * Inicializa la aplicación:
     * 1. Carga el historial de predicciones.
     * 2. Configura el acceso a la cámara web.
     * 3. Configura los listeners de eventos para los botones.
     */

    // Carga el historial
    loadHistory();

    // Configura el acceso a la cámara
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            // ... (código para manejar el stream de video)
        })
        .catch(error => {
            // ... (código para manejar errores de acceso a la cámara)
        });

    // Configura el botón de captura
    const captureButton = document.getElementById('capture');
    if (captureButton) {
        captureButton.addEventListener('click', captureAndPredict);
    } else {
        console.error('Botón de captura no encontrado');
    }

    // Crea y configura el botón para limpiar la caché
    const clearCacheButton = document.createElement('button');
    clearCacheButton.className = 'btn btn-warning mt-3 ml-2';
    clearCacheButton.innerHTML = 'Limpiar Caché de Predicciones';
    clearCacheButton.onclick = clearPredictionCache;

    // Añade el botón de limpiar caché al DOM
    const captureParent = captureButton ? captureButton.parentNode : null;
    if (captureParent) {
        captureParent.appendChild(clearCacheButton);
    } else {
        console.error('Padre del botón de captura no encontrado');
    }
});
