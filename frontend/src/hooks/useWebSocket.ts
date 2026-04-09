import { useEffect, useState, useCallback } from 'react';

interface WebSocketMessage {
  type: string;
  [key: string]: any;
}

export function useWebSocket(onMessage?: (data: WebSocketMessage) => void) {
  const [connected, setConnected] = useState(false);
  const [ws, setWs] = useState<WebSocket | null>(null);

  useEffect(() => {
    const wsUrl = `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}`
      .replace('http', 'ws');
    
    const websocket = new WebSocket(`${wsUrl}/ws`);

    websocket.onopen = () => {
      console.log('WebSocket connected');
      setConnected(true);
    };

    websocket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (onMessage) {
          onMessage(data);
        }
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
      setConnected(false);
    };

    websocket.onclose = () => {
      console.log('WebSocket disconnected');
      setConnected(false);
      // Attempt to reconnect after 3 seconds
      setTimeout(() => {
        // Reconnect logic can be added here
      }, 3000);
    };

    setWs(websocket);

    return () => {
      websocket.close();
    };
  }, [onMessage]);

  const send = useCallback((message: object) => {
    if (ws && connected) {
      ws.send(JSON.stringify(message));
    }
  }, [ws, connected]);

  return { connected, ws, send };
}
