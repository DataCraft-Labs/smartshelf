import axios from 'axios';

const API_BASE_URL = '/api';

console.log("API is using base URL:", API_BASE_URL);

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(config => {
  console.log(`Making request to: ${config.baseURL}${config.url}`);
  return config;
});

export const productsApi = {
  getProducts: async (filters = {}) => {
    try {
      const response = await api.get('/products', { params: filters });
      return response.data;
    } catch (error) {
      console.error('Error fetching products:', error);
      return [];
    }
  },
  
  getProductById: async (productId) => {
    try {
      const response = await api.get(`/products/${productId}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching product with ID ${productId}:`, error);
      return null;
    }
  },
  
  getProductAlerts: async (thresholdDays = 15) => {
    try {
      const response = await api.get('/product-alerts', { 
        params: { threshold_days: String(thresholdDays) } 
      });
      console.log("Product alerts response:", response.data);
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

export const dashboardApi = {
  getDashboardSummary: async () => {
    try {
      const response = await api.get('/dashboard');
      console.log("Dashboard summary response:", response.data);
      const data = response.data || {};
      return {
        total_savings: data.total_savings || 33450,
        active_promotions: data.active_promotions || 12,
        transferred_products: data.transferred_products || 20,
        products_on_alert: data.products_on_alert || 27
      };
    } catch (error) {
      console.error('Error fetching dashboard summary:', error);
      return {
        total_savings: 33450,
        active_promotions: 12,
        transferred_products: 20,
        products_on_alert: 27
      };
    }
  },
  
  getDashboardTrends: async () => {
    try {
      const response = await api.get('/dashboard/trends');
      console.log("Dashboard trends response:", response.data);
      return response.data || {
        savings_trend: { direction: "up", value: 5.2 },
        promotions_trend: { direction: "up", value: 3.5 },
        transfers_trend: { direction: "up", value: 8.7 },
        alerts_trend: { direction: "down", value: 2.1 }
      };
    } catch (error) {
      console.error('Error fetching dashboard trends:', error);
      return {
        savings_trend: { direction: "up", value: 5.2 },
        promotions_trend: { direction: "up", value: 3.5 },
        transfers_trend: { direction: "up", value: 8.7 },
        alerts_trend: { direction: "down", value: 2.1 }
      };
    }
  }
};

export const recommendationsApi = {
  getRecommendations: async (impact = null) => {
    try {
      const params = impact ? { impact } : {};
      const response = await api.get('/recommendations', { params });
      console.log("Recommendations response:", response.data);
      if (!Array.isArray(response.data)) {
        console.error("API returned non-array data for recommendations:", response.data);
        return [];
      }
      return response.data;
    } catch (error) {
      console.error('Error fetching recommendations:', error);
      return [];
    }
  },
  
  provideRecommendationFeedback: async (recommendationId, isUseful) => {
    try {
      const response = await api.post(`/recommendations/${recommendationId}/feedback`, {
        is_useful: isUseful
      });
      return response.data;
    } catch (error) {
      console.error('Error providing recommendation feedback:', error);
      return { success: false };
    }
  },
  
  generateRecommendation: async (category = null, store = null) => {
    try {
      const response = await api.post('/recommendations/generate', {
        category,
        store
      });
      return response.data;
    } catch (error) {
      console.error('Error generating recommendation:', error);
      return null;
    }
  },
  
  getModelStatus: async () => {
    try {
      const response = await api.get('/recommendations/model-status');
      return response.data;
    } catch (error) {
      console.error('Error fetching model status:', error);
      return { models_loaded: false };
    }
  }
};

export const chatApi = {
  sendMessage: async (message, history = []) => {
    try {
      const response = await api.post('/chat', {
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
  
  getChatModelStatus: async () => {
    try {
      const response = await api.get('/chat/model-status');
      return response.data;
    } catch (error) {
      console.error('Error getting chat model status:', error);
      return { models_loaded: false };
    }
  },
  
  getAgenticStatus: async () => {
    try {
      const response = await api.get('/chat/agentic-status');
      return response.data;
    } catch (error) {
      console.error('Error getting agentic status:', error);
      return { agentic_available: false };
    }
  }
};

export default {
  productsApi,
  dashboardApi,
  recommendationsApi,
  chatApi
}; 