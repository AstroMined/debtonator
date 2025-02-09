export interface CashflowForecast {
  date: Date;
  total_bills: number;
  total_income: number;
  balance: number;
  forecast: number;
  min_14_day: number;
  min_30_day: number;
  min_60_day: number;
  min_90_day: number;
}

// For API responses
export interface CashflowForecastResponse {
  date: string;
  total_bills: string | number;
  total_income: string | number;
  balance: string | number;
  forecast: string | number;
  min_14_day: string | number;
  min_30_day: string | number;
  min_60_day: string | number;
  min_90_day: string | number;
}

// Transform API response to frontend model
export const transformCashflowForecast = (data: CashflowForecastResponse): CashflowForecast => {
  return {
    date: new Date(data.date),
    total_bills: typeof data.total_bills === 'string' ? parseFloat(data.total_bills) : data.total_bills,
    total_income: typeof data.total_income === 'string' ? parseFloat(data.total_income) : data.total_income,
    balance: typeof data.balance === 'string' ? parseFloat(data.balance) : data.balance,
    forecast: typeof data.forecast === 'string' ? parseFloat(data.forecast) : data.forecast,
    min_14_day: typeof data.min_14_day === 'string' ? parseFloat(data.min_14_day) : data.min_14_day,
    min_30_day: typeof data.min_30_day === 'string' ? parseFloat(data.min_30_day) : data.min_30_day,
    min_60_day: typeof data.min_60_day === 'string' ? parseFloat(data.min_60_day) : data.min_60_day,
    min_90_day: typeof data.min_90_day === 'string' ? parseFloat(data.min_90_day) : data.min_90_day,
  };
};
