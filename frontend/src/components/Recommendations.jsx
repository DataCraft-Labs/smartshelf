import React, { useState, useEffect } from 'react';
import { recommendationsApi } from '../services/api.js';

const Recommendations = () => {
  const [selectedTab, setSelectedTab] = useState('current');
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [history, setHistory] = useState([
    {
      id: 1,
      title: "Promoção para produtos de pintura",
      description: "Aplicado com sucesso, economia de R$ 1.230",
      date: "06/12/2024"
    },
    {
      id: 2,
      title: "Transferência entre lojas",
      description: "15 produtos transferidos para Jardins",
      date: "01/12/2024"
    },
    {
      id: 3,
      title: "Desconto progressivo",
      description: "75% dos produtos vendidos antes do vencimento",
      date: "28/11/2024"
    },
    {
      id: 4,
      title: "Reorganização de estoque",
      description: "Redução de 12% no tempo de separação",
      date: "25/11/2024"
    },
    {
      id: 5,
      title: "Campanha especial",
      description: "Venda de produtos sazonais com 22% de desconto",
      date: "20/11/2024"
    },
    {
      id: 6,
      title: "Remanejamento de estoque",
      description: "Transferência entre setores reduziu perdas em 15%",
      date: "15/11/2024"
    }
  ]);

  useEffect(() => {
    // Fetch recommendations from API
    const fetchRecommendations = async () => {
      setLoading(true);
      try {
        const data = await recommendationsApi.getRecommendations();
        setRecommendations(data);
        setError(null);
      } catch (err) {
        console.error('Error fetching recommendations:', err);
        setError('Falha ao carregar recomendações');
        // Fallback mock data
        setRecommendations([
          {
            id: 1,
            title: "Realocação de Estoque",
            description: "Transferir produtos da seção Jardim para loja com maior demanda histórica",
            impact: "high",
            is_useful: null
          },
          {
            id: 2,
            title: "Promoção Relâmpago",
            description: "Iniciar promoção para produtos de pintura com menos de 15 dias para vencimento",
            impact: "medium",
            is_useful: null
          },
          {
            id: 3,
            title: "Reabastecimento Estratégico",
            description: "Reduzir compra de produtos sazonais com baixa rotatividade no próximo trimestre",
            impact: "medium", 
            is_useful: null
          },
          {
            id: 4,
            title: "Exposição Especial",
            description: "Criar exposição destacada para itens de jardinagem com vencimento em 20 dias",
            impact: "low",
            is_useful: null
          }
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendations();
  }, []);

  const handleFeedback = async (recommendationId, isUseful) => {
    try {
      // Update local state immediately for UI responsiveness
      setRecommendations(prevRecs => 
        prevRecs.map(rec => 
          rec.id === recommendationId ? { ...rec, is_useful: isUseful } : rec
        )
      );
      
      // Send feedback to API
      await recommendationsApi.provideRecommendationFeedback(recommendationId, isUseful);
    } catch (err) {
      console.error('Error providing feedback:', err);
      // Revert UI state if API call fails
      setRecommendations(prevRecs => 
        prevRecs.map(rec => 
          rec.id === recommendationId ? { ...rec, is_useful: null } : rec
        )
      );
    }
  };
  
  return (
    <div className="flex flex-col h-full">
      <div className="flex border-b border-gray-700 mb-3 p-3">
        <button 
          className={`pb-1.5 px-3 text-sm font-medium ${selectedTab === 'current' ? 'text-primary border-b-2 border-primary' : 'text-gray-400'}`}
          onClick={() => setSelectedTab('current')}
        >
          Recomendações
        </button>
        <button 
          className={`pb-1.5 px-3 text-sm font-medium ${selectedTab === 'history' ? 'text-primary border-b-2 border-primary' : 'text-gray-400'}`}
          onClick={() => setSelectedTab('history')}
        >
          Histórico
        </button>
      </div>
      
      <div 
        className="overflow-y-auto px-3 pb-3" 
        style={{ 
          maxHeight: "450px", 
          height: "450px",
          scrollbarWidth: "thin",
          scrollbarColor: "#4B5563 transparent"
        }}
      >
        {loading ? (
          <div className="text-center py-4">Carregando recomendações...</div>
        ) : error ? (
          <div className="text-center py-4 text-red-400">{error}</div>
        ) : selectedTab === 'current' ? (
          <div className="space-y-3">
            {recommendations.map(recommendation => (
              <div key={recommendation.id} className="bg-gray-800/50 rounded-lg p-3">
                <div className="mb-2">
                  <h3 className="font-medium">{recommendation.title}</h3>
                </div>
                <p className="text-sm text-gray-400 mb-2">
                  {recommendation.description}
                </p>
                {recommendation.impact === "high" && (
                  <div className="p-2 bg-gray-700/50 rounded mb-2">
                    <div className="flex justify-between mb-1">
                      <span className="text-xs text-gray-400">Impacto:</span>
                      <span className="text-xs text-green-400">Alto</span>
                    </div>
                  </div>
                )}
                <div className="mt-2 pt-2 border-t border-gray-700 flex justify-between items-center">
                  <div className="text-sm text-gray-400">
                    Esta sugestão foi útil?
                  </div>
                  <div className="flex space-x-2">
                    <button 
                      className={`inline-flex items-center ${
                        recommendation.is_useful === true 
                          ? 'bg-green-900/40 text-green-300' 
                          : 'bg-green-900/20 hover:bg-green-900/40 text-green-400'
                      } px-2 py-0.5 rounded text-sm`}
                      onClick={() => handleFeedback(recommendation.id, true)}
                      disabled={recommendation.is_useful !== null}
                    >
                      👍
                    </button>
                    <button 
                      className={`inline-flex items-center ${
                        recommendation.is_useful === false 
                          ? 'bg-red-900/40 text-red-300' 
                          : 'bg-red-900/20 hover:bg-red-900/40 text-red-400'
                      } px-2 py-0.5 rounded text-sm`}
                      onClick={() => handleFeedback(recommendation.id, false)}
                      disabled={recommendation.is_useful !== null}
                    >
                      👎
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="space-y-3">
            {history.map(item => (
              <div key={item.id} className="bg-gray-800/30 rounded-lg p-3">
                <div className="flex justify-between mb-1">
                  <p className="text-sm font-medium">{item.title}</p>
                  <span className="text-xs text-gray-500">{item.date}</span>
                </div>
                <p className="text-xs text-gray-400">{item.description}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Recommendations; 