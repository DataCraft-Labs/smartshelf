import React, { useState, useEffect } from 'react';

const AlertTable = ({ alerts }) => {
  // State for pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(6);
  
  // Calculate total number of pages
  const totalItems = alerts.length;
  const totalPages = Math.ceil(totalItems / itemsPerPage);
  
  // Get current items
  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentItems = alerts.slice(indexOfFirstItem, indexOfLastItem);
  
  // Change page
  const paginate = (pageNumber) => setCurrentPage(pageNumber);
  
  // Go to next page
  const nextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1);
    }
  };
  
  // Go to previous page
  const prevPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  };
  
  // Handle items per page change
  const handleItemsPerPageChange = (e) => {
    setItemsPerPage(Number(e.target.value));
    setCurrentPage(1); // Reset to first page when changing items per page
  };
  
  // Reset to page 1 when alerts data changes
  useEffect(() => {
    setCurrentPage(1);
  }, [alerts]);

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full">
        <thead>
          <tr className="border-b border-gray-700">
            <th className="text-left py-1.5 px-4 text-gray-400 font-medium">Produto</th>
            <th className="text-left py-1.5 px-4 text-gray-400 font-medium">Categoria</th>
            <th className="text-left py-1.5 px-4 text-gray-400 font-medium">Dias até Vencer</th>
            <th className="text-left py-1.5 px-4 text-gray-400 font-medium">Quantidade</th>
            <th className="text-left py-1.5 px-4 text-gray-400 font-medium">Loja</th>
            <th className="text-left py-1.5 px-4 text-gray-400 font-medium">Ações</th>
          </tr>
        </thead>
        <tbody>
          {currentItems.length > 0 ? (
            currentItems.map((alert) => (
              <tr key={alert.id} className="border-b border-gray-700">
                <td className="py-2 px-4">{alert.product}</td>
                <td className="py-2 px-4">{alert.category}</td>
                <td className="py-2 px-4">
                  <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium
                    ${alert.daysRemaining <= 7 
                      ? 'bg-red-900/30 text-red-400' // danger
                      : 'bg-amber-900/30 text-amber-400' // warning
                    }`}>
                    {alert.daysRemaining} dias
                  </span>
                </td>
                <td className="py-2 px-4">{alert.quantity} unidades</td>
                <td className="py-2 px-4">{alert.store}</td>
                <td className="py-2 px-4">
                  <div className="flex flex-col space-y-2">
                    <div className="flex space-x-2">
                      <button className="px-2 py-0.5 text-xs bg-primary/20 text-primary rounded hover:bg-primary/30">
                        Transferir
                      </button>
                      <button className="px-2 py-0.5 text-xs bg-warning/20 text-warning rounded hover:bg-warning/30">
                        Promover
                      </button>
                    </div>
                    {alert.recommendedAction && (
                      <div className="text-xs text-gray-400">
                        <span className={`font-medium ${
                          alert.alertLevel === 'high' ? 'text-red-400' : 
                          alert.alertLevel === 'medium' ? 'text-amber-400' : 'text-green-400'
                        }`}>
                          {alert.alertLevel === 'high' ? 'Alta prioridade' : 
                          alert.alertLevel === 'medium' ? 'Média prioridade' : 'Baixa prioridade'}
                        </span>: {alert.recommendedAction}
                      </div>
                    )}
                  </div>
                </td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan="6" className="py-4 text-center text-gray-400">
                Nenhum produto em alerta.
              </td>
            </tr>
          )}
        </tbody>
      </table>
      
      {totalItems > 0 && (
        <div className="flex flex-col md:flex-row md:justify-between items-center px-4 py-2 space-y-2 md:space-y-0">
          <div className="flex items-center space-x-2">
            <div className="text-sm text-gray-400">
              Mostrando <span className="font-medium">{currentItems.length}</span> de <span className="font-medium">{totalItems}</span> produtos
            </div>
            <div className="flex items-center space-x-2">
              <label htmlFor="itemsPerPage" className="text-sm text-gray-400">Mostrar:</label>
              <select
                id="itemsPerPage"
                value={itemsPerPage}
                onChange={handleItemsPerPageChange}
                className="bg-gray-700 text-gray-200 text-sm rounded px-2 py-1 focus:outline-none focus:ring-1 focus:ring-primary"
              >
                <option value={6}>6</option>
                <option value={10}>10</option>
                <option value={20}>20</option>
              </select>
            </div>
          </div>
          
          <div className="flex">
            <button 
              className={`px-3 py-1 rounded-l-md bg-gray-700 text-gray-300 text-sm ${currentPage === 1 ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-600'}`}
              onClick={prevPage}
              disabled={currentPage === 1}
            >
              Anterior
            </button>
            
            {totalPages <= 5 ? (
              // If we have 5 or fewer pages, show all page numbers
              [...Array(totalPages).keys()].map((number) => (
                <button 
                  key={number + 1}
                  className={`px-3 py-1 ${currentPage === number + 1 ? 'bg-primary text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'} text-sm`}
                  onClick={() => paginate(number + 1)}
                >
                  {number + 1}
                </button>
              ))
            ) : (
              // If we have more than 5 pages, show first, current, and last with ellipses
              <>
                {/* First page always visible */}
                <button 
                  className={`px-3 py-1 ${currentPage === 1 ? 'bg-primary text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'} text-sm`}
                  onClick={() => paginate(1)}
                >
                  1
                </button>
                
                {/* Ellipsis before current if needed */}
                {currentPage > 3 && (
                  <span className="px-3 py-1 bg-gray-700 text-gray-300 text-sm">...</span>
                )}
                
                {/* Pages around current */}
                {[...Array(totalPages).keys()]
                  .filter(number => 
                    number + 1 > 1 && // not the first page
                    number + 1 < totalPages && // not the last page
                    Math.abs(number + 1 - currentPage) <= 1 // within 1 of current
                  )
                  .map(number => (
                    <button 
                      key={number + 1}
                      className={`px-3 py-1 ${currentPage === number + 1 ? 'bg-primary text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'} text-sm`}
                      onClick={() => paginate(number + 1)}
                    >
                      {number + 1}
                    </button>
                  ))
                }
                
                {/* Ellipsis after current if needed */}
                {currentPage < totalPages - 2 && (
                  <span className="px-3 py-1 bg-gray-700 text-gray-300 text-sm">...</span>
                )}
                
                {/* Last page always visible */}
                {totalPages > 1 && (
                  <button 
                    className={`px-3 py-1 ${currentPage === totalPages ? 'bg-primary text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'} text-sm`}
                    onClick={() => paginate(totalPages)}
                  >
                    {totalPages}
                  </button>
                )}
              </>
            )}
            
            <button 
              className={`px-3 py-1 rounded-r-md bg-gray-700 text-gray-300 text-sm ${currentPage === totalPages ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-600'}`}
              onClick={nextPage}
              disabled={currentPage === totalPages}
            >
              Próxima
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default AlertTable; 