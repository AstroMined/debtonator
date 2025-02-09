import { configureStore } from '@reduxjs/toolkit';
import accountsReducer from './slices/accountsSlice';
import billsReducer from './slices/billsSlice';
import incomeReducer from './slices/incomeSlice';
import cashflowReducer from './slices/cashflowSlice';

export const store = configureStore({
  reducer: {
    accounts: accountsReducer,
    bills: billsReducer,
    income: incomeReducer,
    cashflow: cashflowReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

// Type-safe hooks
import { TypedUseSelectorHook, useDispatch, useSelector } from 'react-redux';
export const useAppDispatch: () => AppDispatch = useDispatch;
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;
