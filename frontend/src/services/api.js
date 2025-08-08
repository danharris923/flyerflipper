/**
 * API Service
 * 
 * Centralized API client for FlyerFlutter backend communication.
 * Handles authentication, request/response interceptors, and error handling.
 */

import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000, // 30 second timeout
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add any auth tokens if needed in the future
    // const token = localStorage.getItem('authToken');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
    
    // Log requests in development
    if (import.meta.env.DEV) {
      console.warn(`🔄 ${config.method?.toUpperCase()} ${config.url}`, config.params || config.data);
    }
    
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    // Log responses in development
    if (import.meta.env.DEV) {
      console.warn(`✅ ${response.config.method?.toUpperCase()} ${response.config.url}`, response.data);
    }
    
    return response;
  },
  (error) => {
    // Handle common errors
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response;
      
      console.error(`❌ API Error ${status}:`, data);
      
      // Handle specific status codes
      switch (status) {
        case 401:
          // Unauthorized - could redirect to login if auth is implemented
          break;
        case 403:
          // Forbidden
          break;
        case 404:
          // Not found
          break;
        case 429:
          // Rate limited
          console.warn('⚠️ Rate limited - please slow down requests');
          break;
        case 500:
          // Server error
          console.error('🚨 Server error - please try again later');
          break;
        default:
          break;
      }
    } else if (error.request) {
      // Request was made but no response received
      console.error('📶 Network error - please check your connection');
    } else {
      // Something else happened
      console.error('❌ Request setup error:', error.message);
    }
    
    return Promise.reject(error);
  }
);

/**
 * API Service Methods
 */
export const apiService = {
  // Health and Status
  async getHealth() {
    const response = await api.get('/health');
    return response.data;
  },

  async getApiStatus() {
    const response = await api.get('/status');
    return response.data;
  },

  // Stores
  async getNearbyStores({ lat, lng, postal_code, radius = 5000, maxResults = 20, page = 1, perPage = 20 }) {
    const params = {
      radius,
      max_results: maxResults,
      page,
      per_page: perPage
    };

    // Add location parameters - either coordinates or postal code
    if (lat !== undefined && lng !== undefined) {
      params.lat = lat;
      params.lng = lng;
    }
    
    if (postal_code) {
      params.postal_code = postal_code;
    }

    const response = await api.get('/stores', {
      params
    });
    return response.data;
  },

  async getStore(storeId) {
    const response = await api.get(`/stores/${storeId}`);
    return response.data;
  },

  // Deals
  async getDeals(params = {}) {
    const {
      lat,
      lng,
      postalCode,
      query,
      storeId,
      category,
      minDiscount,
      page = 1,
      perPage = 50,
      refresh = false
    } = params;

    const response = await api.get('/deals', {
      params: {
        lat,
        lng,
        postal_code: postalCode,
        query,
        store_id: storeId,
        category,
        min_discount: minDiscount,
        page,
        per_page: perPage,
        refresh
      }
    });
    return response.data;
  },

  async compareDeals(product, postalCode = null) {
    const response = await api.get('/deals/compare', {
      params: {
        product,
        postal_code: postalCode
      }
    });
    return response.data;
  },

  // Testing and Utilities
  async testFlippApi(postalCode = 'K1A0A6', query = 'milk') {
    const response = await api.post('/test-flipp', null, {
      params: {
        postal_code: postalCode,
        query
      }
    });
    return response.data;
  },

  async refreshDeals(postalCode) {
    const response = await api.post('/refresh-deals', null, {
      params: {
        postal_code: postalCode
      }
    });
    return response.data;
  }
};

/**
 * Error handling utility
 */
export const handleApiError = (error) => {
  if (error.response) {
    // Server error with response
    const { status, data } = error.response;
    return {
      type: 'server_error',
      status,
      message: data?.detail || data?.message || `Server error (${status})`,
      data
    };
  } else if (error.request) {
    // Network error
    return {
      type: 'network_error',
      message: 'Unable to connect to server. Please check your internet connection.',
      originalError: error
    };
  } else {
    // Request setup error
    return {
      type: 'request_error',
      message: error.message || 'An unexpected error occurred',
      originalError: error
    };
  }
};

/**
 * Retry utility for failed requests
 */
export const retryRequest = async (requestFn, maxAttempts = 3, delay = 1000) => {
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await requestFn();
    } catch (error) {
      if (attempt === maxAttempts) {
        throw error;
      }
      
      // Don't retry on client errors (4xx)
      if (error.response?.status >= 400 && error.response?.status < 500) {
        throw error;
      }
      
      // Wait before retrying
      await new Promise(resolve => setTimeout(resolve, delay * attempt));
      console.warn(`🔄 Retrying request (attempt ${attempt + 1}/${maxAttempts})`);
    }
  }
};

/**
 * Upload utility (for future use if needed)
 */
export const uploadFile = async (file, endpoint, onProgress = null) => {
  const formData = new FormData();
  formData.append('file', file);

  const config = {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    ...(onProgress && {
      onUploadProgress: (progressEvent) => {
        const percentCompleted = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        onProgress(percentCompleted);
      }
    })
  };

  const response = await api.post(endpoint, formData, config);
  return response.data;
};

export default api;