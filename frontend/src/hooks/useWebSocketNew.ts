import { useEffect, useState, useCallback, useRef } from 'react';

interface WebSocketMessage {
  type: string;
  [key: string]: any;
}

export function useWebSocket(onMessage?: (data: WebSocketMessage) => void) {
  const [connected, setConnected] = useState(false);
  const [ws, setWs] = useState<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 10;

  const connect = useCallback(() => {
    try {
      // Get backend URL and convert to WebSocket URL
      let backendUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      
      // Ensure URL doesn't have trailing slash
      backendUrl = backendUrl.replace(/\/$/, '');
      
      // Convert http/https to ws/wss
      const wsUrl = backendUrl
        .replace(/^https:\/\//, 'wss://')
        .replace(/^http:\/\//, 'ws://');
      
      const wsEndpoint = `${wsUrl}/ws`;
      console.log(`🔌 [WebSocket] Attempting connection to: ${wsEndpoint}`);

      const websocket = new WebSocket(wsEndpoint);

      websocket.onopen = () => {
        console.log('✅ [WebSocket] Connected successfully');
        setConnected(true);
        reconnectAttemptsRef.current = 0;
        
        // Send initial ping
        try {
          websocket.send('ping');
        } catch (e) {
          console.warn('Could not send initial ping:', e);
        }
      };

      websocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('📨 [WebSocket] Message received:', data);
          if (onMessage) {
            onMessage(data);
          }
        } catch (error) {
          console.error('❌ [WebSocket] Failed to parse message:', error);
        }
      };

      websocket.onerror = (error) => {
        console.error('❌ [WebSocket] Error detected:', error);
        console.error('WebSocket readyState:', websocket.readyState);
        setConnected(false);
      };

      websocket.onclose = (event) => {
        console.log(`⚠️ [WebSocket] Connection closed (code: ${event.code}, clean: ${event.wasClean})`);
        setConnected(false);
        
        // Attempt to reconnect with exponential backoff
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          const delay = 1000 * Math.pow(1.5, reconnectAttemptsRef.current);
          console.log(`🔄 [WebSocket] Reconnecting in ${Math.round(delay)}ms (attempt ${reconnectAttemptsRef.current + 1}/${maxReconnectAttempts})`);
          reconnectAttemptsRef.current++;
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, delay);
        } else {
          console.error('❌ [WebSocket] Max reconnection attempts reached');
        }
      };

      setWs(websocket);
    } catch (error) {
      console.error('❌ [WebSocket] Connection error:', error);
      setConnected(false);
    }
  }, [onMessage]);

  useEffect(() => {
    connect();
    
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (ws) {
        ws.close();
      }
    };
  }, [connect, ws]);

  const send = useCallback((message: object) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      try {
        ws.send(JSON.stringify(message));
        console.log('📤 [WebSocket] Message sent:', message);
      } catch (error) {
        console.error('❌ [WebSocket] Failed to send message:', error);
      }
    } else {
      console.warn('⚠️ [WebSocket] Cannot send - connection not open (readyState:', ws?.readyState, ')');
    }
  }, [ws]);

  return { connected, ws, send };
}
