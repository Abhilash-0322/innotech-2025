import { create } from 'zustand';

interface User {
  email: string;
  full_name: string;
  role: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isHydrated: boolean;
  setAuth: (user: User, token: string) => void;
  clearAuth: () => void;
  hydrate: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  isAuthenticated: false,
  isHydrated: false,
  
  setAuth: (user, token) => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('user', JSON.stringify(user));
      localStorage.setItem('token', token);
    }
    set({ user, token, isAuthenticated: true, isHydrated: true });
  },
  
  clearAuth: () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('user');
      localStorage.removeItem('token');
    }
    set({ user: null, token: null, isAuthenticated: false, isHydrated: true });
  },
  
  hydrate: () => {
    if (typeof window !== 'undefined') {
      const user = localStorage.getItem('user');
      const token = localStorage.getItem('token');
      if (user && token) {
        set({ user: JSON.parse(user), token, isAuthenticated: true, isHydrated: true });
      } else {
        set({ isHydrated: true });
      }
    }
  },
}));
