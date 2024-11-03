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
    const history = JSON.parse(localStorage.getItem('predictionHistory')) || [];
    const historyList = document.getElementById('historyList');
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
}

// Función para guardar una nueva predicción
function savePrediction(prediction) {
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
}

// Función para limpiar la caché de predicciones
function clearPredictionCache() {
    Object.keys(localStorage).forEach(key => {
        if (key !== 'predictionHistory') {
            localStorage.removeItem(key);
        }
    });
    alert('Caché de predicciones limpiada');
}

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    // Cargar el historial al iniciar la página
    loadHistory();

    // Acceder a la cámara
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            document.getElementById('video').srcObject = stream;
        })
        .catch(error => {
            console.error('Error al acceder a la cámara:', error);
            document.getElementById('apiData').innerHTML = 'No se pudo acceder a la cámara.';
        });

    // Capturar imagen y enviar a la API
    document.getElementById('capture').addEventListener('click', () => {
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        canvas.width = document.getElementById('video').videoWidth;
        canvas.height = document.getElementById('video').videoHeight;
        ctx.drawImage(document.getElementById('video'), 0, 0, canvas.width, canvas.height);

        const imageData = canvas.toDataURL('image/png');
        const imageHash = simpleHash(imageData);

        // Verificar si ya tenemos una predicción para esta imagen en localStorage
        const cachedPrediction = localStorage.getItem(imageHash);
        if (cachedPrediction) {
            const prediction = JSON.parse(cachedPrediction);
            document.getElementById('apiData').innerHTML = `(Caché) La imagen se clasificó como ${prediction.class}`;
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
        .then(response => response.json())
        .then(data => {
            document.getElementById('apiData').innerHTML = `La imagen se clasificó como ${data.class}`;
            localStorage.setItem(imageHash, JSON.stringify(data));
            savePrediction(data);
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('apiData').innerHTML = 'Error al realizar la predicción: ' + error;
        });
    });

    // Añadir botón para limpiar caché
    const clearCacheButton = document.createElement('button');
    clearCacheButton.className = 'btn btn-warning mt-3 ml-2';
    clearCacheButton.innerHTML = 'Limpiar Caché de Predicciones';
    clearCacheButton.onclick = clearPredictionCache;
    document.getElementById('capture').parentNode.appendChild(clearCacheButton);
});