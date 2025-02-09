import React, { useEffect, useState, useCallback } from 'react';
import { getCashflowForecast, getCashflowHistory, getAccountBalanceHistory } from '../../services/cashflow';
import { getAccounts } from '../../services/accounts';
import { CashflowForecast } from '../../types/cashflow';
import { Account } from '../../types/accounts';
import CashflowDisplay from './CashflowDisplay';

export const CashflowDisplayContainer: React.FC = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [currentData, setCurrentData] = useState<CashflowForecast | undefined>(undefined);
  const [historicalData, setHistoricalData] = useState<CashflowForecast[]>([]);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [selectedDateRange, setSelectedDateRange] = useState<[Date, Date]>(() => {
    const end = new Date();
    const start = new Date();
    start.setDate(start.getDate() - 90); // Default to 90 days
    return [start, end];
  });

  const fetchHistoricalData = useCallback(async (start: Date, end: Date) => {
    try {
      const data = await getCashflowHistory(start, end);
      setHistoricalData(data);
    } catch (err) {
      console.error('Failed to fetch historical data:', err);
    }
  }, []);

  const handleDateRangeChange = useCallback(async (start: Date, end: Date) => {
    setSelectedDateRange([start, end]);
    await fetchHistoricalData(start, end);
  }, [fetchHistoricalData]);

  const handleAccountToggle = useCallback(async (accountId: number) => {
    try {
      const [start, end] = selectedDateRange;
      await getAccountBalanceHistory(accountId, start, end);
      // Note: In a real implementation, we would update the account balance data in state
    } catch (err) {
      console.error('Failed to fetch account history:', err);
    }
  }, [selectedDateRange]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        const [forecast, accountsList] = await Promise.all([
          getCashflowForecast(),
          getAccounts()
        ]);
        
        setCurrentData(forecast);
        setAccounts(accountsList);
        
        // Fetch initial historical data
        const [start, end] = selectedDateRange;
        await fetchHistoricalData(start, end);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to fetch cashflow data'));
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();

    // Set up polling every 5 minutes to keep data fresh
    const intervalId = setInterval(() => {
      getCashflowForecast()
        .then(setCurrentData)
        .catch(console.error);
    }, 5 * 60 * 1000);

    return () => clearInterval(intervalId);
  }, [fetchHistoricalData, selectedDateRange]);

  return (
    <CashflowDisplay
      isLoading={isLoading}
      error={error}
      currentData={currentData}
      historicalData={historicalData}
      accounts={accounts}
      onDateRangeChange={handleDateRangeChange}
      onAccountToggle={handleAccountToggle}
    />
  );
};

export default CashflowDisplayContainer;
