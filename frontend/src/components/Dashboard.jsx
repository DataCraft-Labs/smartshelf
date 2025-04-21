import React, { useState, useEffect } from 'react';
import MetricCard from './MetricCard.jsx';
import AlertTable from './AlertTable.jsx';
import Recommendations from './Recommendations.jsx';
import ChatWidget from './ChatWidget.jsx';
import { dashboardApi, productsApi } from '../services/api.js';

// Icons
import { 
  ArrowUpIcon, 
  CheckCircleIcon, 
  ExclamationTriangleIcon,
  MagnifyingGlassIcon
} from '@heroicons/react/24/outline';

const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState({
    totalSavings: 0,
    activePromotions: 0,
    transferredProducts: 0,
    productsOnAlert: 0
  });
  
  const [trendData, setTrendData] = useState({
    savings_trend: { direction: "up", value: 0 },
    promotions_trend: { direction: "up", value: 0 },
    transfers_trend: { direction: "up", value: 0 },
    alerts_trend: { direction: "down", value: 0 }
  });
  
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    // Fetch dashboard data and product alerts from API
    const fetchDashboardData = async () => {
      setLoading(true);
      try {
        // Get dashboard summary data
        const dashboardResponse = await dashboardApi.getDashboardSummary();
        console.log("Dashboard data:", dashboardResponse);
        
        setDashboardData({
          totalSavings: dashboardResponse.total_savings || 0,
          activePromotions: dashboardResponse.active_promotions || 0,
          transferredProducts: dashboardResponse.transferred_products || 0,
          productsOnAlert: dashboardResponse.products_on_alert || 0
        });
        
        // Get trend data for dashboard metrics
        const trendsResponse = await dashboardApi.getDashboardTrends();
        console.log("Trends data:", trendsResponse);
        setTrendData(trendsResponse);
        
        // Get products on alert
        const alertsResponse = await productsApi.getProductAlerts();
        console.log("Alerts data:", alertsResponse);
        
        // Map API response to expected format with fallback for missing values
        if (Array.isArray(alertsResponse)) {
          const formattedAlerts = alertsResponse.map(alert => {
            // Check if product is an object, otherwise initialize empty object
            const product = alert.product || {};
            
            // Extract properties directly from product object, with fallbacks
            return {
              id: product.id || alert.id || Math.random().toString(36).substr(2, 9),
              product: product.name || (typeof product === 'string' ? product : "Produto sem nome"),
              category: product.category || "Sem categoria",
              daysRemaining: product.days_until_expiry || alert.days_until_expiry || 0,
              quantity: product.quantity || 0,
              store: product.store || "Loja não especificada",
              alertLevel: alert.alert_level || "medium",
              recommendedAction: alert.recommended_action || "Monitorar estoque"
            };
          }).filter(alert => alert.id); // Filter out invalid items
          
          setAlerts(formattedAlerts);
        } else {
          // Fallback if alertsResponse is not an array
          setAlerts([]);
          console.error("Expected array for alerts, got:", alertsResponse);
        }
        
        setError(null);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Falha ao carregar dados. Por favor, tente novamente.');
        
        // Fallback to mock data in case of API error
        setDashboardData({
          totalSavings: 33450,
          activePromotions: 12,
          transferredProducts: 20,
          productsOnAlert: 27
        });
        
        setAlerts([
          { id: 1, product: 'Tinta Acrílica Fosca', category: 'Pintura', daysRemaining: 15, quantity: 45, store: 'Vila Mariana' },
          { id: 2, product: 'Verniz Marítimo', category: 'Pintura', daysRemaining: 15, quantity: 23, store: 'Pinheiros' },
          { id: 3, product: 'Buquê Primavera', category: 'Jardim', daysRemaining: 7, quantity: 18, store: 'Jardins' },
          { id: 4, product: 'Suculenta', category: 'Jardim', daysRemaining: 7, quantity: 20, store: 'Jardins' },
          { id: 5, product: 'Cola de contato', category: 'Pintura', daysRemaining: 15, quantity: 7, store: 'Vila Mariana' },
          { id: 6, product: 'Fertilizante Natural', category: 'Jardim', daysRemaining: 12, quantity: 15, store: 'Pinheiros' },
          { id: 7, product: 'Impermeabilizante', category: 'Pintura', daysRemaining: 10, quantity: 8, store: 'Jardins' },
          { id: 8, product: 'Massa Corrida', category: 'Pintura', daysRemaining: 14, quantity: 12, store: 'Vila Mariana' },
          { id: 9, product: 'Orquídea Phalaenopsis', category: 'Jardim', daysRemaining: 5, quantity: 10, store: 'Pinheiros' },
          { id: 10, product: 'Selador Acrílico', category: 'Pintura', daysRemaining: 8, quantity: 18, store: 'Jardins' }
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  // Filter alerts based on search query
  const filteredAlerts = searchQuery
    ? alerts.filter(alert => 
        alert.product.toLowerCase().includes(searchQuery.toLowerCase()) ||
        alert.category.toLowerCase().includes(searchQuery.toLowerCase()) ||
        alert.store.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : alerts;

  // Format the total savings value safely
  const formatTotalSavings = () => {
    try {
      return `R$ ${dashboardData.totalSavings.toLocaleString('pt-BR')}`;
    } catch (error) {
      console.error('Error formatting total savings:', error);
      return `R$ ${0}`;
    }
  };

  return (
    <div className="space-y-5 p-2 max-w-7xl mx-auto">
      <div>
        <h2 className="text-xl font-semibold mb-3 px-4">Visão Geral do Estoque</h2>
      </div>
      
      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="max-w-full w-full">
          <MetricCard 
            title="Economia Total" 
            value={formatTotalSavings()} 
            icon={<ArrowUpIcon className="w-5 h-5" />}
            color="bg-surface"
            titleIcon={<ArrowUpIcon className="w-5 h-5 text-green-500" />}
            valueColor="text-green-500"
            isLoading={loading}
            trend={trendData.savings_trend.direction}
            trendValue={trendData.savings_trend.value}
          />
        </div>
        <div className="max-w-full w-full">
          <MetricCard 
            title="Promoções Ativas" 
            value={String(dashboardData.activePromotions || 0)} 
            icon={<CheckCircleIcon className="w-5 h-5" />}
            color="bg-surface"
            titleIcon={<CheckCircleIcon className="w-5 h-5 text-green-500" />}
            isLoading={loading}
            trend={trendData.promotions_trend.direction}
            trendValue={trendData.promotions_trend.value}
          />
        </div>
        <div className="max-w-full w-full">
          <MetricCard 
            title="Produtos Transferidos" 
            value={String(dashboardData.transferredProducts || 0)} 
            icon={<CheckCircleIcon className="w-5 h-5" />}
            color="bg-surface"
            titleIcon={<CheckCircleIcon className="w-5 h-5 text-green-500" />}
            isLoading={loading}
            trend={trendData.transfers_trend.direction}
            trendValue={trendData.transfers_trend.value}
          />
        </div>
        <div className="max-w-full w-full">
          <MetricCard 
            title="Produtos em Alerta" 
            value={String(dashboardData.productsOnAlert || 0)} 
            icon={<ExclamationTriangleIcon className="w-5 h-5" />}
            color="bg-surface"
            titleIcon={<ExclamationTriangleIcon className="w-5 h-5 text-warning" />}
            valueColor="text-warning"
            isLoading={loading}
            trend={trendData.alerts_trend.direction}
            trendValue={trendData.alerts_trend.value}
          />
        </div>
      </div>

      <div>
        <h2 className="text-xl font-semibold mb-3 px-4">Gestão de Produtos</h2>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Alert Table - 2/3 width */}
        <div className="lg:col-span-2 bg-surface rounded-lg overflow-hidden">
          <div className="p-3 border-b border-gray-700 flex items-center justify-between">
            <div className="flex items-center">
              <ExclamationTriangleIcon className="w-5 h-5 text-warning mr-2" />
              <h2 className="text-lg font-semibold">Produtos em Alerta de Vencimento</h2>
            </div>
            <div className="relative">
              <input
                type="text"
                placeholder="Buscar..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9 pr-4 py-1 bg-gray-700 rounded-full text-sm w-64 focus:outline-none focus:ring-1 focus:ring-primary"
              />
              <MagnifyingGlassIcon className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            </div>
          </div>
          <div>
            {loading ? (
              <p className="text-center py-4">Carregando dados...</p>
            ) : error ? (
              <p className="text-center py-4 text-red-400">{error}</p>
            ) : (
              <AlertTable alerts={filteredAlerts} />
            )}
          </div>
        </div>

        {/* Recommendations - 1/3 width */}
        <div className="lg:col-span-1 bg-surface rounded-lg overflow-hidden flex flex-col h-full">
          <div className="p-3 border-b border-gray-700 flex items-center">
            <svg className="w-5 h-5 text-warning mr-2" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path strokeLinecap="round" strokeLinejoin="round" d="M13 9l3 3m0 0l-3 3m3-3H8m13 0a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h2 className="text-lg font-semibold">Ações Recomendadas</h2>
          </div>
          <div className="flex-grow overflow-hidden">
            {loading ? (
              <p className="text-center py-4">Carregando dados...</p>
            ) : (
              <Recommendations />
            )}
          </div>
        </div>
      </div>

      {/* Chat Widget - Always shown at bottom right */}
      <ChatWidget />
    </div>
  );
};

export default Dashboard; 