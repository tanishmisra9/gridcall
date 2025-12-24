// API client for connecting to FastAPI backend

import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if it exists
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Handle 401 errors globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      if (typeof window !== 'undefined') {
        localStorage.removeItem('token');
        // Redirect to login if not already there
        if (window.location.pathname !== '/login' && window.location.pathname !== '/register') {
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

// Types
export interface User {
  id: number;
  username: string;
  email: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Race {
  id: number;
  year: number;
  round_number: number;
  location: string;
  race_date: string;
  predictions_close: string;
  completed: boolean;
  results_processed: boolean;
}

export interface UpcomingRace extends Race {
  time_until_close: string;
  can_predict: boolean;
}

export interface Prediction {
  race_id: number;
  pole_driver: string;
  podium_p1: string;
  podium_p2: string;
  podium_p3: string;
  chaser_driver?: string;
  breakout_type: 'driver' | 'team';
  breakout_name: string;
  bust_type: 'driver' | 'team';
  bust_name: string;
  full_send_category?: string;
}

export interface UserPrediction extends Prediction {
  id: number;
  submitted_at: string;
  points_earned: number;
  scored: boolean;
}

export interface Grid {
  id: number;
  name: string;
  invite_code: string;
  created_by: number;
  member_count: number;
}

// Auth Functions
export const register = async (username: string, email: string, password: string): Promise<AuthResponse> => {
  const response = await api.post('/api/users/register', { username, email, password });
  return response.data;
};

export const login = async (email: string, password: string): Promise<AuthResponse> => {
  const response = await api.post('/api/users/login', { email, password });
  return response.data;
};

export const getCurrentUser = async (): Promise<User> => {
  const response = await api.get('/api/users/me');
  return response.data;
};

// Races
export const getUpcomingRaces = async (): Promise<UpcomingRace[]> => {
  const response = await api.get('/api/races/upcoming');
  return response.data;
};

export const getRace = async (raceId: number): Promise<Race> => {
  const response = await api.get(`/api/races/${raceId}`);
  return response.data;
};

// Predictions
export const submitPrediction = async (prediction: Prediction): Promise<UserPrediction> => {
  const response = await api.post('/api/predictions/', prediction);
  return response.data;
};

export const updatePrediction = async (
  predictionId: number,
  prediction: Prediction
): Promise<UserPrediction> => {
  const response = await api.put(`/api/predictions/${predictionId}`, prediction);
  return response.data;
};

export const getMyPrediction = async (raceId: number): Promise<UserPrediction> => {
  const response = await api.get(`/api/predictions/user/me/race/${raceId}`);
  return response.data;
};

export const getRacePredictions = async (raceId: number): Promise<UserPrediction[]> => {
  const response = await api.get(`/api/predictions/race/${raceId}`);
  return response.data;
};

// Grids
export const createGrid = async (name: string): Promise<Grid> => {
  const response = await api.post('/api/grids/', { name });
  return response.data;
};

export const joinGrid = async (inviteCode: string): Promise<Grid> => {
  const response = await api.post(`/api/grids/${inviteCode}/join`);
  return response.data;
};

export const getMyGrids = async (): Promise<Grid[]> => {
  const response = await api.get('/api/grids/my');
  return response.data;
};

export default api;
