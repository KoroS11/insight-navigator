// =============================================================================
// API Client - Centralized fetch wrapper with auth & 401 handling
// =============================================================================

import { ApiError, TokenResponse } from '@/types/api';

// -----------------------------------------------------------------------------
// Configuration
// -----------------------------------------------------------------------------

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const TOKEN_KEY = 'nsa_access_token';
const REFRESH_TOKEN_KEY = 'nsa_refresh_token';

// -----------------------------------------------------------------------------
// Token Management
// -----------------------------------------------------------------------------

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}

export function isAuthenticated(): boolean {
  return !!getToken();
}

// -----------------------------------------------------------------------------
// Refresh Token Logic
// -----------------------------------------------------------------------------

let isRefreshing = false;
let refreshPromise: Promise<boolean> | null = null;

async function attemptTokenRefresh(): Promise<boolean> {
  // Prevent multiple simultaneous refresh attempts
  if (isRefreshing && refreshPromise) {
    return refreshPromise;
  }

  isRefreshing = true;
  refreshPromise = (async () => {
    try {
      const currentToken = getToken();
      if (!currentToken) {
        return false;
      }

      const response = await fetch(`${API_BASE_URL}/api/v1/auth/refresh`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${currentToken}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        return false;
      }

      const data: TokenResponse = await response.json();
      setToken(data.access_token);
      return true;
    } catch {
      return false;
    } finally {
      isRefreshing = false;
      refreshPromise = null;
    }
  })();

  return refreshPromise;
}

// -----------------------------------------------------------------------------
// Core Fetch Wrapper
// -----------------------------------------------------------------------------

interface FetchOptions extends RequestInit {
  skipAuth?: boolean;
}

export async function fetchApi<T>(
  endpoint: string,
  options: FetchOptions = {}
): Promise<T> {
  const { skipAuth = false, ...fetchOptions } = options;

  const url = endpoint.startsWith('http') 
    ? endpoint 
    : `${API_BASE_URL}${endpoint.startsWith('/') ? '' : '/'}${endpoint}`;

  const headers: HeadersInit = {
    ...(fetchOptions.headers || {}),
  };

  // Only set Content-Type for requests with a body
  const hasBody = fetchOptions.body !== undefined;
  if (hasBody) {
    (headers as Record<string, string>)['Content-Type'] = 'application/json';
  }

  // Add auth header if we have a token and auth isn't skipped
  if (!skipAuth) {
    const token = getToken();
    if (token) {
      (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
    }
  }

  const response = await fetch(url, {
    ...fetchOptions,
    headers,
  });

  // Handle 401 - attempt refresh and retry
  if (response.status === 401 && !skipAuth) {
    const refreshed = await attemptTokenRefresh();
    
    if (refreshed) {
      // Retry the original request with new token
      const newToken = getToken();
      if (newToken) {
        (headers as Record<string, string>)['Authorization'] = `Bearer ${newToken}`;
      }
      
      const retryResponse = await fetch(url, {
        ...fetchOptions,
        headers,
      });

      if (!retryResponse.ok) {
        const errorData = await retryResponse.json().catch(() => null);
        throw new ApiError(retryResponse.status, retryResponse.statusText, errorData);
      }

      // Handle 204 No Content - callers expecting void should use fetchApi<void>
      if (retryResponse.status === 204) {
        return undefined as unknown as T;
      }

      return retryResponse.json();
    } else {
      // Refresh failed - clear token and redirect to login
      clearToken();
      window.location.href = '/login';
      throw new ApiError(401, 'Session expired');
    }
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    throw new ApiError(response.status, response.statusText, errorData);
  }

  // Handle 204 No Content - callers expecting void should use fetchApi<void>
  if (response.status === 204) {
    return undefined as unknown as T;
  }

  return response.json();
}

// -----------------------------------------------------------------------------
// OAuth2 Login (form-urlencoded)
// -----------------------------------------------------------------------------

export async function loginWithCredentials(
  username: string,
  password: string
): Promise<TokenResponse> {
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);
  formData.append('grant_type', 'password');

  const response = await fetch(`${API_BASE_URL}/api/v1/auth/token`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    throw new ApiError(response.status, response.statusText, errorData);
  }

  const data: TokenResponse = await response.json();
  setToken(data.access_token);
  return data;
}

// -----------------------------------------------------------------------------
// Convenience Methods
// -----------------------------------------------------------------------------

export const api = {
  get: <T>(endpoint: string, options?: FetchOptions) =>
    fetchApi<T>(endpoint, { ...options, method: 'GET' }),

  post: <T>(endpoint: string, body?: unknown, options?: FetchOptions) =>
    fetchApi<T>(endpoint, {
      ...options,
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    }),

  patch: <T>(endpoint: string, body?: unknown, options?: FetchOptions) =>
    fetchApi<T>(endpoint, {
      ...options,
      method: 'PATCH',
      body: body ? JSON.stringify(body) : undefined,
    }),

  put: <T>(endpoint: string, body?: unknown, options?: FetchOptions) =>
    fetchApi<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
    }),

  delete: <T>(endpoint: string, options?: FetchOptions) =>
    fetchApi<T>(endpoint, { ...options, method: 'DELETE' }),
};

export default api;
