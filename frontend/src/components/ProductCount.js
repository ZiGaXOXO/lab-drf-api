import React, { useEffect, useState } from 'react';

function ProductCount() {
  const [count, setCount] = useState(null);
  useEffect(() => {
    // Формируем URL: если используется https, ws:// меняется на wss://
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const host = window.location.host; // localhost:8000
    const socketUrl = `${protocol}://${host}/ws/products/count/`;
    const socket = new WebSocket(socketUrl);

    socket.onopen = () => {
      console.log('WebSocket connected');
    };
    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.available_count !== undefined) {
          setCount(data.available_count);
        }
      } catch (e) {
        console.error('Invalid JSON', e);
      }
    };
    socket.onclose = () => {
      console.log('WebSocket disconnected');
    };
    socket.onerror = (err) => {
      console.error('WebSocket error', err);
    };
    // Очистка при unmount
    return () => {
      socket.close();
    };
  }, []);

  return (
    <div>
      <h3>Доступных товаров: {count !== null ? count : 'загрузка...'}</h3>
    </div>
  );
}

export default ProductCount;
