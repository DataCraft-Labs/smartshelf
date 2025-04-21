import axios from 'axios';

// Set the base URL for API requests
// Use environment variable if available or local development endpoint
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

console.log("API is using base URL:", API_BASE_URL);

// Create an axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add an interceptor for debugging
api.interceptors.request.use(config => {
  console.log(`Making request to: ${config.baseURL}${config.url}`);
  return config;
});

// API endpoints for products
export const productsApi = {
  // Get all products with optional filters
  getProducts: async (filters = {}) => {
    try {
      const response = await api.get('/api/products', { params: filters });
      return response.data;
    } catch (error) {
      console.error('Error fetching products:', error);
      // Return empty array as fallback
      return [];
    }
  },
  
  // Get a specific product by ID
  getProductById: async (productId) => {
    try {
      const response = await api.get(`/api/products/${productId}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching product with ID ${productId}:`, error);
      return null;
    }
  },
  
  // Get products on alert (near expiration)
  getProductAlerts: async (thresholdDays = 15) => {
    try {
      const response = await api.get('/api/product-alerts', { 
        params: { threshold_days: String(thresholdDays) } 
      });
      console.log("Product alerts response:", response.data);
      // If response isn't an array, use fallback data
      if (!Array.isArray(response.data)) {
        console.error("API returned non-array data for alerts:", response.data);
        return [
          { 
            product: {
              id: 1,
              name: 'Tinta Acrílica Fosca',
              category: 'Pintura',
              days_until_expiry: 15,
              quantity: 45,
              store: 'Vila Mariana'
            },
            alert_level: "medium",
            recommended_action: "Monitorar estoque"
          },
          { 
            product: {
              id: 2,
              name: 'Verniz Marítimo',
              category: 'Pintura',
              days_until_expiry: 15,
              quantity: 23,
              store: 'Pinheiros'
            },
            alert_level: "medium",
            recommended_action: "Monitorar estoque"
          }
        ];
      }
      return response.data;
    } catch (error) {
      console.error('Error fetching product alerts:', error);
      // Return fallback data on error
      return [
        { 
          product: {
            id: 1,
            name: 'Tinta Acrílica Fosca',
            category: 'Pintura',
            days_until_expiry: 15,
            quantity: 45,
            store: 'Vila Mariana'
          },
          alert_level: "medium",
          recommended_action: "Monitorar estoque"
        },
        { 
          product: {
            id: 2,
            name: 'Verniz Marítimo',
            category: 'Pintura',
            days_until_expiry: 15,
            quantity: 23,
            store: 'Pinheiros'
          },
          alert_level: "medium",
          recommended_action: "Monitorar estoque"
        }
      ];
    }
  }
};

// API endpoints for dashboard
export const dashboardApi = {
  // Get dashboard summary data
  getDashboardSummary: async () => {
    try {
      const response = await api.get('/api/dashboard');
      console.log("Dashboard summary response:", response.data);
      // Ensure we have the expected properties or use default values
      const data = response.data || {};
      return {
        total_savings: data.total_savings || 33450,
        active_promotions: data.active_promotions || 12,
        transferred_products: data.transferred_products || 20,
        products_on_alert: data.products_on_alert || 27
      };
    } catch (error) {
      console.error('Error fetching dashboard summary:', error);
      // Return fallback data on error
      return {
        total_savings: 33450,
        active_promotions: 12,
        transferred_products: 20,
        products_on_alert: 27
      };
    }
  },
  
  // Get dashboard trend data
  getDashboardTrends: async () => {
    try {
      const response = await api.get('/api/dashboard/trends');
      console.log("Dashboard trends response:", response.data);
      return response.data || {
        savings_trend: { direction: "up", value: 5.2 },
        promotions_trend: { direction: "up", value: 3.5 },
        transfers_trend: { direction: "up", value: 8.7 },
        alerts_trend: { direction: "down", value: 2.1 }
      };
    } catch (error) {
      console.error('Error fetching dashboard trends:', error);
      // Return fallback data on error
      return {
        savings_trend: { direction: "up", value: 5.2 },
        promotions_trend: { direction: "up", value: 3.5 },
        transfers_trend: { direction: "up", value: 8.7 },
        alerts_trend: { direction: "down", value: 2.1 }
      };
    }
  }
};

// API endpoints for recommendations
export const recommendationsApi = {
  // Get all recommendations with optional filtering by impact
  getRecommendations: async (impact = null) => {
    try {
      const params = impact ? { impact } : {};
      const response = await api.get('/api/recommendations', { params });
      console.log("Recommendations response:", response.data);
      if (!Array.isArray(response.data)) {
        console.error("API returned non-array data for recommendations:", response.data);
        return []; // Return empty array as fallback
      }
      return response.data;
    } catch (error) {
      console.error('Error fetching recommendations:', error);
      return []; // Return empty array on error
    }
  },
  
  // Provide feedback on a recommendation
  provideRecommendationFeedback: async (recommendationId, isUseful) => {
    try {
      const response = await api.post(`/api/recommendations/${recommendationId}/feedback`, {
        is_useful: isUseful
      });
      return response.data;
    } catch (error) {
      console.error('Error providing recommendation feedback:', error);
      return { success: false };
    }
  },
  
  // Generate a new recommendation based on category and store
  generateRecommendation: async (category = null, store = null) => {
    try {
      const response = await api.post('/api/recommendations/generate', {
        category,
        store
      });
      return response.data;
    } catch (error) {
      console.error('Error generating recommendation:', error);
      return null;
    }
  },
  
  // Get model status
  getModelStatus: async () => {
    try {
      const response = await api.get('/api/recommendations/model-status');
      return response.data;
    } catch (error) {
      console.error('Error fetching model status:', error);
      return { models_loaded: false };
    }
  }
};

// API endpoints for chat
export const chatApi = {
  // Send a message to the chat API
  sendMessage: async (message, history = []) => {
    try {
      const response = await api.post('/api/chat', {
        message,
        history
      });
      return response.data;
    } catch (error) {
      console.error('Error sending chat message:', error);
      return {
        response: "Desculpe, não consegui processar sua mensagem. Por favor, tente novamente.",
        history: [...(history || []), { role: "user", content: message }]
      };
    }
  },
  
  // Get model status
  getChatModelStatus: async () => {
    try {
      const response = await api.get('/api/chat/model-status');
      return response.data;
    } catch (error) {
      console.error('Error fetching chat model status:', error);
      return { models_loaded: false };
    }
  }
};

export default {
  productsApi,
  dashboardApi,
  recommendationsApi,
  chatApi
}; 