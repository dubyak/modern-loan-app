/**
 * Authentication Store using Zustand
 */

import { create } from 'zustand';
import { authAPI, usersAPI } from '@/lib/api';

export interface User {
  id: string;
  phone: string;
  role: 'customer' | 'agent' | 'admin';
  status: 'active' | 'inactive' | 'suspended';
  first_name?: string;
  last_name?: string;
  created_at: string;
  updated_at: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;

  // Actions
  login: (phone: string, password: string) => Promise<void>;
  register: (data: { phone: string; password: string; first_name?: string; last_name?: string }) => Promise<void>;
  logout: () => void;
  loadUser: () => Promise<void>;
  setUser: (user: User) => void;
  setToken: (token: string) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  isLoading: false,
  isAuthenticated: false,

  login: async (phone: string, password: string) => {
    set({ isLoading: true });
    try {
      const response = await authAPI.login({ phone, password });
      const { access_token, user } = response.data;

      localStorage.setItem('access_token', access_token);
      localStorage.setItem('user', JSON.stringify(user));

      set({
        user,
        token: access_token,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  register: async (data) => {
    set({ isLoading: true });
    try {
      const response = await authAPI.register(data);
      const { access_token, user } = response.data;

      localStorage.setItem('access_token', access_token);
      localStorage.setItem('user', JSON.stringify(user));

      set({
        user,
        token: access_token,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');

    set({
      user: null,
      token: null,
      isAuthenticated: false,
    });
  },

  loadUser: async () => {
    const token = localStorage.getItem('access_token');
    const userStr = localStorage.getItem('user');

    if (!token || !userStr) {
      set({ isAuthenticated: false, isLoading: false });
      return;
    }

    try {
      // Verify token is still valid by fetching current user
      const response = await usersAPI.getCurrentUser();
      const user = response.data;

      set({
        user,
        token,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (error) {
      // Token invalid, clear storage
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');

      set({
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
      });
    }
  },

  setUser: (user) => set({ user }),
  setToken: (token) => set({ token }),
}));
