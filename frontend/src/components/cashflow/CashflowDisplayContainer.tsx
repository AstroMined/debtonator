import React, { useEffect, useState } from 'react';
import { getCashflowForecast } from '../../services/cashflow';
import { CashflowForecast } from '../../types/cashflow';
import CashflowDisplay from './CashflowDisplay';

export const CashflowDisplayContainer: React.FC = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [data, setData] = useState<CashflowForecast | undefined>(undefined);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const forecast = await getCashflowForecast();
        setData(forecast);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to fetch cashflow data'));
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();

    // Set up polling every 5 minutes to keep data fresh
    const intervalId = setInterval(fetchData, 5 * 60 * 1000);

    return () => clearInterval(intervalId);
  }, []);

  return (
    <CashflowDisplay
      isLoading={isLoading}
      error={error}
      data={data}
    />
  );
};

export default CashflowDisplayContainer;
