/**
 * AgroVision API client.
 * Centralises axios configuration, token injection, and error handling.
 * All feature modules import from this file — never configure axios elsewhere.
 */

import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import type { ErrorResponse } from '@/types';

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api/v1';

function createApiClient(): AxiosInstance {
  const client = axios.create({
    baseURL: BASE_URL,
    timeout: 30_000,
    headers: { 'Content-Type': 'application/json' },
  });

  client.interceptors.request.use((config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  });

  client.interceptors.response.use(
    (response) => response,
    async (error: AxiosError<ErrorResponse>) => {
      if (error.response?.status === 401) {
        // TODO: attempt token refresh; if refresh fails, redirect to /login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
      return Promise.reject(error);
    }
  );

  return client;
}

export const apiClient = createApiClient();
