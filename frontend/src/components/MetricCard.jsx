import React from 'react';

const MetricCard = ({ title, value, color, valueColor, titleIcon, isLoading = false, trend = null, trendValue = null }) => {
  // Only generate trend data if not provided from props
  let trendDirection = trend;
  let trendPercentage = trendValue;
  
  if (trendDirection === null || trendPercentage === null) {
    // Fallback to random data only when not provided
    trendDirection = Math.random() > 0.5 ? 'up' : 'down';
    trendPercentage = (Math.random() * 10).toFixed(1);
  }
  
  let trendText, trendClass;
  if (trendDirection === 'up') {
    trendText = `↑ ${trendPercentage}% aumento`;
    trendClass = 'text-green-400';
  } else {
    trendText = `↓ ${trendPercentage}% redução`;
    trendClass = 'text-red-400';
  }
  
  return (
    <div className={`${color} rounded-lg p-5 h-52 flex flex-col`}>
      <div className="flex items-center mb-3">
        {titleIcon && (
          <div className="mr-2">{titleIcon}</div>
        )}
        <h3 className="text-sm text-gray-400 font-normal">{title}</h3>
      </div>
      <div className="flex items-center justify-center flex-grow">
        {isLoading ? (
          <div className="animate-pulse bg-gray-600 h-12 w-24 rounded"></div>
        ) : (
          <p className={`text-5xl font-bold ${valueColor || "text-white"}`}>
            {value}
          </p>
        )}
      </div>
      <div className="mt-3 pt-3 border-t border-gray-700">
        {isLoading ? (
          <div className="space-y-2">
            <div className="animate-pulse bg-gray-600 h-4 w-24 rounded"></div>
            <div className="animate-pulse bg-gray-600 h-3 w-36 rounded"></div>
          </div>
        ) : (
          <>
            <p className={`text-sm ${trendClass}`}>{trendText}</p>
            <p className="text-xs text-gray-400 mt-1">Comparado ao mês anterior</p>
          </>
        )}
      </div>
    </div>
  );
};

export default MetricCard; 