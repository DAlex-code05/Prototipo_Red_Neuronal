// main.js

// Función para calcular un hash simple de la imagen
function simpleHash(imageData) {
    let hash = 0;
    for (let i = 0; i < imageData.length; i++) {
        const char = imageData.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash; // Convierte a un entero de 32 bits
    }
    return hash;
}

// Función para cargar el historial guardado
function loadHistory() {
    try {
        const history = JSON.parse(localStorage.getItem('predictionHistory')) || [];
        const historyList = document.getElementById('historyList');
        if (!historyList) {
            console.error('Elemento historyList no encontrado');
            return;
        }
        historyList.innerHTML = '';
        
        history.forEach(prediction => {
            const item = document.createElement('div');
            item.className = 'list-group-item';
            item.innerHTML = `
                <p>Animal: ${prediction.class}</p>
                <p>Confianza: ${(prediction.confidence * 100).toFixed(2)}%</p>
                <p>Fecha: ${prediction.date}</p>
            `;
            historyList.prepend(item);
        });
    } catch (error) {
        console.error('Error al cargar el historial:', error);
    }
}

// Función para guardar una nueva predicción
function savePrediction(prediction) {
    try {
        const history = JSON.parse(localStorage.getItem('predictionHistory')) || [];
        const newPrediction = {
            ...prediction,
            date: new Date().toLocaleString()
        };
        
        history.push(newPrediction);
        
        // Mantener solo las últimas 10 predicciones
        if (history.length > 10) {
            history.shift();
        }
        
        localStorage.setItem('predictionHistory', JSON.stringify(history));
        loadHistory();
    } catch (error) {
        console.error('Error al guardar la predicción:', error);
    }
}

// Función para limpiar la caché de predicciones
function clearPredictionCache() {
    try {
        Object.keys(localStorage).forEach(key => {
            if (key !== 'predictionHistory') {
                localStorage.removeItem(key);
            }
        });
        alert('Caché de predicciones limpiada');
    } catch (error) {
        console.error('Error al limpiar la caché:', error);
        alert('Error al limpiar la caché de predicciones');
    }
}

// Función para capturar imagen y enviar a la API
function captureAndPredict() {
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const apiData = document.getElementById('apiData');
    
    if (!video || !canvas || !apiData) {
        console.error('Elementos de video, canvas o apiData no encontrados');
        return;
    }

    const ctx = canvas.getContext('2d');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const imageData = canvas.toDataURL('image/png');
    const imageHash = simpleHash(imageData);

    // Verificar si ya tenemos una predicción para esta imagen en localStorage
    const cachedPrediction = localStorage.getItem(imageHash);
    if (cachedPrediction) {
        const prediction = JSON.parse(cachedPrediction);
        apiData.innerHTML = `(Caché) La imagen se clasificó como ${prediction.class}`;
        savePrediction(prediction);
        return;
    }

    // Si no está en caché, enviar a la API
    fetch('/api/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ image: imageData }),
    })
    .then(response => {
        if (!response.ok) {
            return response.text().then(text => {
                throw new Error(`HTTP error! status: ${response.status}, message: ${text}`);
            });
        }
        return response.json();
    })
    .then(data => {
        apiData.innerHTML = `La imagen se clasificó como ${data.class}`;
        localStorage.setItem(imageHash, JSON.stringify(data));
        savePrediction(data);
    })
    .catch(error => {
        console.error('Error:', error);
        apiData.innerHTML = 'Error al realizar la predicción: ' + error.message;
    });
}

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    loadHistory();

    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            const video = document.getElementById('video');
            if (video) {
                video.srcObject = stream;
            } else {
                console.error('Elemento de video no encontrado');
            }
        })
        .catch(error => {
            console.error('Error al acceder a la cámara:', error);
            const apiData = document.getElementById('apiData');
            if (apiData) {
                apiData.innerHTML = 'No se pudo acceder a la cámara.';
            }
        });

    const captureButton = document.getElementById('capture');
    if (captureButton) {
        captureButton.addEventListener('click', captureAndPredict);
    } else {
        console.error('Botón de captura no encontrado');
    }

    const clearCacheButton = document.createElement('button');
    clearCacheButton.className = 'btn btn-warning mt-3 ml-2';
    clearCacheButton.innerHTML = 'Limpiar Caché de Predicciones';
    clearCacheButton.onclick = clearPredictionCache;

    const captureParent = captureButton ? captureButton.parentNode : null;
    if (captureParent) {
        captureParent.appendChild(clearCacheButton);
    } else {
        console.error('Padre del botón de captura no encontrado');
    }
});
