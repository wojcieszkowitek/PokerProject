const WebSocket = require('ws');

// Adres Twojego serwera FastAPI
const url = 'ws://localhost:8000/ws/test';
const connection = new WebSocket(url);

// 1. Gdy połączenie zostanie otwarte
connection.on('open', () => {
    console.log('✅ Połączono z serwerem!');
    connection.send('Siema z Node.js!');
});

// 2. Gdy serwer coś do nas wyśle
connection.on('message', (data) => {
    console.log(`📩 Wiadomość od serwera: ${data}`);
});

// 3. Obsługa błędów
connection.on('error', (error) => {
    console.error(`❌ Błąd: ${error.message}`);
});