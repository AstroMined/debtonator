import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { Account, AccountUpdate } from '../../types/accounts';
import { Decimal } from 'decimal.js';

interface BalanceHistoryEntry {
  timestamp: Date;
  balance: Decimal;
}

interface AccountsState {
  accounts: Account[];
  balanceHistory: Record<number, BalanceHistoryEntry[]>;
  loading: boolean;
  error: string | null;
}

const initialState: AccountsState = {
  accounts: [],
  balanceHistory: {},
  loading: false,
  error: null,
};

const accountsSlice = createSlice({
  name: 'accounts',
  initialState,
  reducers: {
    setAccounts: (state, action: PayloadAction<Account[]>) => {
      state.accounts = action.payload;
      state.loading = false;
      state.error = null;
    },
    addAccount: (state, action: PayloadAction<Account>) => {
      state.accounts.push(action.payload);
    },
    updateAccount: (state, action: PayloadAction<{ id: number; updates: AccountUpdate }>) => {
      const { id, updates } = action.payload;
      const account = state.accounts.find(acc => acc.id === id);
      if (account) {
        Object.assign(account, updates);
        account.updated_at = new Date();
      }
    },
    updateBalance: (state, action: PayloadAction<{ id: number; amount: Decimal; isCredit?: boolean }>) => {
      const { id, amount, isCredit = false } = action.payload;
      const account = state.accounts.find(acc => acc.id === id);
      if (account) {
        // For credit accounts, adding to balance means reducing available credit
        const newBalance = new Decimal(account.available_balance)[isCredit ? 'minus' : 'plus'](amount);
        account.available_balance = newBalance;
        if (account.type === 'credit' && account.available_credit !== null && account.total_limit) {
          account.available_credit = new Decimal(account.total_limit).minus(newBalance);
        }
        account.updated_at = new Date();

        // Update balance history
        if (!state.balanceHistory[id]) {
          state.balanceHistory[id] = [];
        }
        state.balanceHistory[id].push({
          timestamp: new Date(),
          balance: newBalance
        });

        // Keep only last 30 entries
        if (state.balanceHistory[id].length > 30) {
          state.balanceHistory[id] = state.balanceHistory[id].slice(-30);
        }
      }
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
  setAccounts,
  addAccount,
  updateAccount,
  updateBalance,
  setLoading,
  setError,
} = accountsSlice.actions;

export default accountsSlice.reducer;

// Selectors
export const selectAccounts = (state: { accounts: AccountsState }) => state.accounts.accounts;
export const selectAccountById = (state: { accounts: AccountsState }, id: number) =>
  state.accounts.accounts.find(account => account.id === id);
export const selectLoading = (state: { accounts: AccountsState }) => state.accounts.loading;
export const selectError = (state: { accounts: AccountsState }) => state.accounts.error;
export const selectAccountBalanceHistory = (state: { accounts: AccountsState }, accountId: number) =>
  state.accounts.balanceHistory[accountId] || [];
export const selectTotalAvailableCredit = (state: { accounts: AccountsState }) =>
  state.accounts.accounts
    .filter(account => account.type === 'credit' && account.available_credit !== null)
    .reduce((total, account) => total.plus(account.available_credit!), new Decimal(0));
export const selectTotalAvailableBalance = (state: { accounts: AccountsState }) =>
  state.accounts.accounts
    .filter(account => account.type !== 'credit')
    .reduce((total, account) => total.plus(account.available_balance), new Decimal(0));
