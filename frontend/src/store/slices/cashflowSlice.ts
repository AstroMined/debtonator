import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { CashflowForecast } from '../../types/cashflow';

interface CashflowState {
  forecasts: CashflowForecast[];
  selectedDate: Date | null;
  loading: boolean;
  error: string | null;
  dateRange: {
    startDate?: Date;
    endDate?: Date;
  };
}

const initialState: CashflowState = {
  forecasts: [],
  selectedDate: null,
  loading: false,
  error: null,
  dateRange: {},
};

const cashflowSlice = createSlice({
  name: 'cashflow',
  initialState,
  reducers: {
    setForecasts: (state, action: PayloadAction<CashflowForecast[]>) => {
      state.forecasts = action.payload;
      state.loading = false;
      state.error = null;
    },
    addForecast: (state, action: PayloadAction<CashflowForecast>) => {
      state.forecasts.push(action.payload);
    },
    updateForecast: (state, action: PayloadAction<{ date: Date; updates: Partial<CashflowForecast> }>) => {
      const { date, updates } = action.payload;
      const forecast = state.forecasts.find(f => f.date.getTime() === date.getTime());
      if (forecast) {
        Object.assign(forecast, updates);
      }
    },
    setSelectedDate: (state, action: PayloadAction<Date | null>) => {
      state.selectedDate = action.payload;
    },
    setDateRange: (state, action: PayloadAction<CashflowState['dateRange']>) => {
      state.dateRange = action.payload;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
      if (action.payload) {
        state.error = null;
      }
    },
    setError: (state, action: PayloadAction<string>) => {
      state.error = action.payload;
      state.loading = false;
    },
  },
});

export const {
  setForecasts,
  addForecast,
  updateForecast,
  setSelectedDate,
  setDateRange,
  setLoading,
  setError,
} = cashflowSlice.actions;

export default cashflowSlice.reducer;

// Selectors
export const selectForecasts = (state: { cashflow: CashflowState }) => state.cashflow.forecasts;
export const selectSelectedDate = (state: { cashflow: CashflowState }) => state.cashflow.selectedDate;
export const selectLoading = (state: { cashflow: CashflowState }) => state.cashflow.loading;
export const selectError = (state: { cashflow: CashflowState }) => state.cashflow.error;
export const selectDateRange = (state: { cashflow: CashflowState }) => state.cashflow.dateRange;

export const selectFilteredForecasts = (state: { cashflow: CashflowState }) => {
  const { forecasts, dateRange } = state.cashflow;
  return forecasts.filter(forecast => {
    if (dateRange.startDate && forecast.date < dateRange.startDate) return false;
    if (dateRange.endDate && forecast.date > dateRange.endDate) return false;
    return true;
  });
};

export const selectForecastByDate = (state: { cashflow: CashflowState }, date: Date) =>
  state.cashflow.forecasts.find(forecast => forecast.date.getTime() === date.getTime());

export const selectMinimumRequirements = (state: { cashflow: CashflowState }) => {
  const forecasts = state.cashflow.forecasts;
  if (forecasts.length === 0) return null;

  const latestForecast = forecasts[forecasts.length - 1];
  return {
    min14Day: latestForecast.min_14_day,
    min30Day: latestForecast.min_30_day,
    min60Day: latestForecast.min_60_day,
    min90Day: latestForecast.min_90_day,
  };
};

export const selectTotalForecast = (state: { cashflow: CashflowState }) =>
  state.cashflow.forecasts.reduce((total, forecast) => total + forecast.forecast, 0);
