import axios from 'axios';
import { CashflowForecast, CashflowForecastResponse, transformCashflowForecast } from '../types/cashflow';

const BASE_URL = '/api/v1/cashflow';

export const getCashflowForecast = async (): Promise<CashflowForecast> => {
  try {
    const response = await axios.get<CashflowForecastResponse>(`${BASE_URL}/forecast`);
    return transformCashflowForecast(response.data);
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch cashflow forecast');
    }
    throw error;
  }
};

export const getCashflowHistory = async (
  startDate: Date,
  endDate: Date
): Promise<CashflowForecast[]> => {
  try {
    const response = await axios.get<CashflowForecastResponse[]>(`${BASE_URL}/forecast/range`, {
      params: {
        start_date: startDate.toISOString().split('T')[0],
        end_date: endDate.toISOString().split('T')[0],
      },
    });
    return Array.isArray(response.data) 
      ? response.data.map(transformCashflowForecast)
      : [transformCashflowForecast(response.data as CashflowForecastResponse)];
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch cashflow for date range');
    }
    throw error;
  }
};

export const getAccountBalanceHistory = async (
  accountId: number,
  startDate: Date,
  endDate: Date
): Promise<{ date: Date; balance: number }[]> => {
  try {
    const response = await axios.get(`${BASE_URL}/accounts/${accountId}/history`, {
      params: {
        start_date: startDate.toISOString().split('T')[0],
        end_date: endDate.toISOString().split('T')[0],
      },
    });
    return response.data.map((item: { date: string; balance: string }) => ({
      date: new Date(item.date),
      balance: parseFloat(item.balance),
    }));
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch account balance history');
    }
    throw error;
  }
};
