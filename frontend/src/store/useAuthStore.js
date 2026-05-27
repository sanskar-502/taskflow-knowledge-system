/**
 * Auth store using Zustand.
 *
 * Manages the current user session, persists token and user data
 * in localStorage, and provides login/logout actions that the
 * rest of the app can call without worrying about storage details.
 */

import { create } from "zustand";
import api from "../api/axios";

const useAuthStore = create((set) => ({
  user: JSON.parse(localStorage.getItem("user")) || null,
  token: localStorage.getItem("token") || null,
  isAuthenticated: !!localStorage.getItem("token"),
  loading: false,
  error: null,

  login: async (email, password) => {
    set({ loading: true, error: null });
    try {
      const response = await api.post("/auth/login", { email, password });
      const { access_token, user } = response.data;

      localStorage.setItem("token", access_token);
      localStorage.setItem("user", JSON.stringify(user));

      set({
        user,
        token: access_token,
        isAuthenticated: true,
        loading: false,
      });

      return true;
    } catch (error) {
      const message =
        error.response?.data?.detail || "Login failed. Please try again.";
      set({ error: message, loading: false });
      return false;
    }
  },

  logout: () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    set({
      user: null,
      token: null,
      isAuthenticated: false,
      error: null,
    });
  },

  clearError: () => set({ error: null }),
}));

export default useAuthStore;
