import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { Income, IncomeTableRow } from '../../types/income';

interface IncomeState {
  incomeEntries: IncomeTableRow[];
  selectedIncome: Income | null;
  loading: boolean;
  error: string | null;
  filters: {
    startDate?: string;
    endDate?: string;
    source?: string;
    depositStatus?: boolean;
    targetAccountId?: number;
  };
}

const initialState: IncomeState = {
  incomeEntries: [],
  selectedIncome: null,
  loading: false,
  error: null,
  filters: {},
};

const incomeSlice = createSlice({
  name: 'income',
  initialState,
  reducers: {
    setIncomeEntries: (state, action: PayloadAction<IncomeTableRow[]>) => {
      state.incomeEntries = action.payload;
      state.loading = false;
      state.error = null;
    },
    addIncome: (state, action: PayloadAction<IncomeTableRow>) => {
      state.incomeEntries.push(action.payload);
    },
    updateIncome: (state, action: PayloadAction<{ id: number; updates: Partial<Income> }>) => {
      const { id, updates } = action.payload;
      const income = state.incomeEntries.find(inc => inc.id === id);
      if (income) {
        Object.assign(income, updates);
        // Update undeposited amount if deposit status changes
        if ('deposited' in updates) {
          income.undeposited_amount = updates.deposited ? 0 : income.amount;
        }
      }
    },
    setSelectedIncome: (state, action: PayloadAction<Income | null>) => {
      state.selectedIncome = action.payload;
    },
    updateDepositStatus: (state, action: PayloadAction<{ id: number; deposited: boolean }>) => {
      const { id, deposited } = action.payload;
      const income = state.incomeEntries.find(inc => inc.id === id);
      if (income) {
        income.deposited = deposited;
        income.undeposited_amount = deposited ? 0 : income.amount;
      }
    },
    setFilters: (state, action: PayloadAction<IncomeState['filters']>) => {
      state.filters = action.payload;
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
  setIncomeEntries,
  addIncome,
  updateIncome,
  setSelectedIncome,
  updateDepositStatus,
  setFilters,
  setLoading,
  setError,
} = incomeSlice.actions;

export default incomeSlice.reducer;

// Selectors
export const selectIncomeEntries = (state: { income: IncomeState }) => state.income.incomeEntries;
export const selectSelectedIncome = (state: { income: IncomeState }) => state.income.selectedIncome;
export const selectIncomeById = (state: { income: IncomeState }, id: number) =>
  state.income.incomeEntries.find(income => income.id === id);
export const selectLoading = (state: { income: IncomeState }) => state.income.loading;
export const selectError = (state: { income: IncomeState }) => state.income.error;
export const selectFilters = (state: { income: IncomeState }) => state.income.filters;

export const selectFilteredIncome = (state: { income: IncomeState }) => {
  const { incomeEntries, filters } = state.income;
  return incomeEntries.filter(income => {
    if (filters.startDate && income.date < filters.startDate) return false;
    if (filters.endDate && income.date > filters.endDate) return false;
    if (filters.source && !income.source.toLowerCase().includes(filters.source.toLowerCase())) return false;
    if (filters.depositStatus !== undefined && income.deposited !== filters.depositStatus) return false;
    if (filters.targetAccountId !== undefined && income.target_account_id !== filters.targetAccountId) return false;
    return true;
  });
};

export const selectTotalUndepositedAmount = (state: { income: IncomeState }) =>
  state.income.incomeEntries
    .filter(income => !income.deposited)
    .reduce((total, income) => total + income.amount, 0);
