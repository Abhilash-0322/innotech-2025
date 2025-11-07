import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export interface LoginCredentials {
  username: string; // email
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  full_name: string;
  role?: string;
}

export interface User {
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
}

export interface SensorData {
  temperature: number;
  humidity: number;
  smoke_level: number;
  rain_level: number;
  rain_detected: boolean;
  timestamp: string;
  fire_risk_score?: number;
  risk_level?: string;
}

export interface Alert {
  id: string;
  title: string;
  message: string;
  severity: string;
  status: string;
  timestamp: string;
}

export interface DashboardStats {
  current_temperature: number;
  current_humidity: number;
  current_smoke: number;
  current_risk_level: string;
  current_risk_score: number;
  active_alerts: number;
  sprinkler_status: string;
  total_readings_today: number;
  average_temp_today: number;
  max_risk_today: number;
}

// Auth API
export const authAPI = {
  login: async (credentials: LoginCredentials) => {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    const response = await api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
  
  register: async (data: RegisterData) => {
    const response = await api.post('/auth/register', data);
    return response.data;
  },
  
  getMe: async (): Promise<User> => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};

// Dashboard API
export const dashboardAPI = {
  getStats: async (): Promise<DashboardStats> => {
    const response = await api.get('/dashboard/stats');
    return response.data;
  },
  
  getChartData: async (hours: number = 24) => {
    const response = await api.get(`/dashboard/chart-data?hours=${hours}`);
    return response.data;
  },
  
  getRiskAnalysis: async (limit: number = 10) => {
    const response = await api.get(`/dashboard/risk-analysis?limit=${limit}`);
    return response.data;
  },
};

// Sensors API
export const sensorsAPI = {
  getLatest: async (): Promise<SensorData> => {
    const response = await api.get('/sensors/latest');
    return response.data;
  },
  
  getHistory: async (hours: number = 24, limit: number = 100) => {
    const response = await api.get(`/sensors/history?hours=${hours}&limit=${limit}`);
    return response.data;
  },
  
  getStatistics: async (hours: number = 24) => {
    const response = await api.get(`/sensors/statistics?hours=${hours}`);
    return response.data;
  },
};

// Alerts API
export const alertsAPI = {
  getAll: async (status?: string, hours: number = 24, limit: number = 50) => {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    params.append('hours', hours.toString());
    params.append('limit', limit.toString());
    const response = await api.get(`/alerts?${params.toString()}`);
    return response.data;
  },
  
  getActive: async () => {
    const response = await api.get('/alerts/active');
    return response.data;
  },
  
  acknowledge: async (alertId: string) => {
    const response = await api.patch(`/alerts/${alertId}/acknowledge`);
    return response.data;
  },
  
  resolve: async (alertId: string) => {
    const response = await api.patch(`/alerts/${alertId}/resolve`);
    return response.data;
  },
  
  getCounts: async () => {
    const response = await api.get('/alerts/count');
    return response.data;
  },
};

// Sprinkler API
export const sprinklerAPI = {
  getStatus: async () => {
    const response = await api.get('/sprinkler/status');
    return response.data;
  },
  
  control: async (action: string, reason?: string) => {
    const response = await api.post('/sprinkler/control', null, {
      params: { action, reason },
    });
    return response.data;
  },
  
  setAuto: async () => {
    const response = await api.post('/sprinkler/auto');
    return response.data;
  },
  
  getHistory: async (limit: number = 50) => {
    const response = await api.get(`/sprinkler/history?limit=${limit}`);
    return response.data;
  },
};

// WebSocket connection
export class WebSocketClient {
  private ws: WebSocket | null = null;
  private url: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 3000;

  constructor() {
    this.url = (process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000') + '/ws';
  }

  connect(onMessage: (data: any) => void, onError?: (error: Event) => void) {
    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        console.log('✅ WebSocket connected');
        this.reconnectAttempts = 0;
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          onMessage(data);
        } catch (e) {
          console.error('Failed to parse WebSocket message:', e);
        }
      };

      this.ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
        if (onError) onError(error);
      };

      this.ws.onclose = () => {
        console.log('🔌 WebSocket disconnected');
        this.reconnect(onMessage, onError);
      };
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
    }
  }

  private reconnect(onMessage: (data: any) => void, onError?: (error: Event) => void) {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Reconnecting... Attempt ${this.reconnectAttempts}`);
      setTimeout(() => this.connect(onMessage, onError), this.reconnectDelay);
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  send(data: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }
}
