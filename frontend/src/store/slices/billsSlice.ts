import { createSlice, PayloadAction, createSelector, createAsyncThunk } from '@reduxjs/toolkit';
import { 
  Bill,
  BillTableRow, 
  BillCalculations, 
  BillFilters,
  BillUpdatePayload,
  BillSplitUpdatePayload,
  BillPaymentUpdatePayload,
  BillStatus
} from '../../types/bills';
import * as billsApi from '../../services/bills';

// Utility function to convert Bill to BillTableRow
const toBillTableRow = (bill: Bill): BillTableRow => {
  const dueDate = bill.due_date ? new Date(bill.due_date) : new Date();
  const today = new Date();
  const daysOverdue = !bill.paid ? 
    Math.floor((today.getTime() - dueDate.getTime()) / (1000 * 60 * 60 * 24)) : 
    0;

  let status: BillStatus = 'unpaid';
  if (bill.paid) {
    status = 'paid';
  } else if (daysOverdue > 0) {
    status = 'overdue';
  }

  return {
    ...bill,
    status,
    daysOverdue
  };
};

// Async Thunks
export const fetchBills = createAsyncThunk(
  'bills/fetchBills',
  async (dateRange?: { start_date: string; end_date: string }) => {
    const response = await billsApi.getBills(dateRange);
    return response.map(toBillTableRow);
  }
);

export const updateBillPaymentAsync = createAsyncThunk(
  'bills/updateBillPayment',
  async (payload: BillPaymentUpdatePayload, { rejectWithValue }) => {
    try {
      const response = await billsApi.updateBillPaymentStatus(payload.billId, payload.paid);
      return toBillTableRow(response);
    } catch (error) {
      return rejectWithValue((error as Error).message);
    }
  }
);

export const updateBillAsync = createAsyncThunk(
  'bills/updateBill',
  async (payload: BillUpdatePayload, { rejectWithValue }) => {
    try {
      const response = await billsApi.updateBill(payload.id, payload.updates);
      return toBillTableRow(response);
    } catch (error) {
      return rejectWithValue((error as Error).message);
    }
  }
);

interface PendingUpdate {
  type: 'payment' | 'update';
  originalData: BillTableRow;
  timestamp: string;
}

interface BillsState {
  pendingUpdates: Record<number, PendingUpdate>;
  items: Record<number, BillTableRow>;
  selectedBillId: number | null;
  loading: boolean;
  error: string | null;
  filters: BillFilters;
  calculations: BillCalculations;
  lastUpdated: string;
}

const initialCalculations: BillCalculations = {
  totalAmount: 0,
  totalUnpaid: 0,
  totalByAccount: {},
  totalByStatus: {
    paid: 0,
    unpaid: 0,
    overdue: 0
  },
  upcomingBills: 0,
  overdueBills: 0,
  lastUpdated: new Date().toISOString()
};

const initialState: BillsState = {
  pendingUpdates: {},
  items: {},
  selectedBillId: null,
  loading: false,
  error: null,
  filters: {},
  calculations: initialCalculations,
  lastUpdated: new Date().toISOString()
};

const calculateBillsState = (bills: Record<number, BillTableRow>): BillCalculations => {
  const calculations: BillCalculations = {
    totalAmount: 0,
    totalUnpaid: 0,
    totalByAccount: {},
    totalByStatus: {
      paid: 0,
      unpaid: 0,
      overdue: 0
    },
    upcomingBills: 0,
    overdueBills: 0,
    lastUpdated: new Date().toISOString()
  };

  Object.values(bills).forEach(bill => {
    // Total amount
    calculations.totalAmount += bill.amount;

    // Total by status
    calculations.totalByStatus[bill.status]++;

    // Total unpaid
    if (!bill.paid) {
      calculations.totalUnpaid += bill.amount;
    }

    // Total by account (including splits)
    const addToAccount = (accountId: number, amount: number) => {
      calculations.totalByAccount[accountId] = (calculations.totalByAccount[accountId] || 0) + amount;
    };

    // Main account
    addToAccount(bill.account_id, bill.amount - (bill.splits?.reduce((sum, split) => sum + split.amount, 0) || 0));

    // Split accounts
    bill.splits?.forEach(split => {
      addToAccount(split.account_id, split.amount);
    });

    // Upcoming and overdue
    if (bill.daysOverdue > 0) {
      calculations.overdueBills++;
    } else if (!bill.paid) {
      calculations.upcomingBills++;
    }
  });

  return calculations;
};

const billsSlice = createSlice({
  name: 'bills',
  initialState,
  reducers: {
    setBills: (state, action: PayloadAction<BillTableRow[]>) => {
      state.items = action.payload.reduce((acc, bill) => {
        acc[bill.id!] = bill;
        return acc;
      }, {} as Record<number, BillTableRow>);
      state.loading = false;
      state.error = null;
      state.calculations = calculateBillsState(state.items);
      state.lastUpdated = new Date().toISOString();
    },
    addBill: (state, action: PayloadAction<BillTableRow>) => {
      if (action.payload.id) {
        state.items[action.payload.id] = action.payload;
        state.calculations = calculateBillsState(state.items);
        state.lastUpdated = new Date().toISOString();
      }
    },
    updateBill: (state, action: PayloadAction<BillUpdatePayload>) => {
      const { id, updates } = action.payload;
      if (state.items[id]) {
        state.items[id] = { ...state.items[id], ...updates };
        state.calculations = calculateBillsState(state.items);
        state.lastUpdated = new Date().toISOString();
      }
    },
    setSelectedBillId: (state, action: PayloadAction<number | null>) => {
      state.selectedBillId = action.payload;
    },
    updateBillSplits: (state, action: PayloadAction<BillSplitUpdatePayload>) => {
      const { billId, splits } = action.payload;
      if (state.items[billId]) {
        state.items[billId].splits = splits;
        state.items[billId].splitAmounts = splits.reduce((acc, split) => {
          acc[split.account_id] = split.amount;
          return acc;
        }, {} as { [accountId: number]: number });
        state.calculations = calculateBillsState(state.items);
        state.lastUpdated = new Date().toISOString();
      }
    },
    updatePaymentStatus: (state, action: PayloadAction<BillPaymentUpdatePayload>) => {
      const { billId, paid, paidDate } = action.payload;
      if (state.items[billId]) {
        const bill = state.items[billId];
        bill.paid = paid;
        if (paid && paidDate) {
          bill.paid_date = paidDate;
        } else {
          bill.paid_date = undefined;
        }
        bill.status = paid ? 'paid' : bill.daysOverdue > 0 ? 'overdue' : 'unpaid';
        state.calculations = calculateBillsState(state.items);
        state.lastUpdated = new Date().toISOString();
      }
    },
    setFilters: (state, action: PayloadAction<BillFilters>) => {
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
    recalculateState: (state) => {
      state.calculations = calculateBillsState(state.items);
      state.lastUpdated = new Date().toISOString();
    }
  },
  extraReducers: (builder) => {
    // Fetch Bills
    builder
      .addCase(fetchBills.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchBills.fulfilled, (state, action) => {
        state.items = action.payload.reduce((acc, bill) => {
          acc[bill.id!] = bill;
          return acc;
        }, {} as Record<number, BillTableRow>);
        state.loading = false;
        state.error = null;
        state.calculations = calculateBillsState(state.items);
        state.lastUpdated = new Date().toISOString();
      })
      .addCase(fetchBills.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch bills';
      })

    // Update Bill Payment
    builder
      .addCase(updateBillPaymentAsync.pending, (state, action) => {
        const { billId, paid } = action.meta.arg;
        if (state.items[billId]) {
          // Store original state for rollback
          state.pendingUpdates[billId] = {
            type: 'payment',
            originalData: { ...state.items[billId] },
            timestamp: new Date().toISOString()
          };
          // Optimistically update
          state.items[billId].paid = paid;
          state.items[billId].status = paid ? 'paid' : 
            state.items[billId].daysOverdue > 0 ? 'overdue' : 'unpaid';
          state.calculations = calculateBillsState(state.items);
        }
      })
      .addCase(updateBillPaymentAsync.fulfilled, (state, action) => {
        const billId = action.meta.arg.billId;
        // Clear pending update
        delete state.pendingUpdates[billId];
        // Update with server response
        if (action.payload.id) {
          state.items[action.payload.id] = {
            ...state.items[action.payload.id],
            ...action.payload
          };
          state.calculations = calculateBillsState(state.items);
        }
      })
      .addCase(updateBillPaymentAsync.rejected, (state, action) => {
        const billId = action.meta.arg.billId;
        // Rollback on failure
        if (state.pendingUpdates[billId]) {
          state.items[billId] = state.pendingUpdates[billId].originalData;
          delete state.pendingUpdates[billId];
          state.calculations = calculateBillsState(state.items);
        }
        state.error = action.error.message || 'Failed to update payment status';
      })

    // Update Bill
    builder
      .addCase(updateBillAsync.pending, (state, action) => {
        const { id } = action.meta.arg;
        if (state.items[id]) {
          // Store original state for rollback
          state.pendingUpdates[id] = {
            type: 'update',
            originalData: { ...state.items[id] },
            timestamp: new Date().toISOString()
          };
          // Optimistically update
          state.items[id] = { ...state.items[id], ...action.meta.arg.updates };
          state.calculations = calculateBillsState(state.items);
        }
      })
      .addCase(updateBillAsync.fulfilled, (state, action) => {
        const billId = action.meta.arg.id;
        // Clear pending update
        delete state.pendingUpdates[billId];
        // Update with server response
        if (action.payload.id) {
          state.items[action.payload.id] = {
            ...state.items[action.payload.id],
            ...action.payload
          };
          state.calculations = calculateBillsState(state.items);
        }
      })
      .addCase(updateBillAsync.rejected, (state, action) => {
        const billId = action.meta.arg.id;
        // Rollback on failure
        if (state.pendingUpdates[billId]) {
          state.items[billId] = state.pendingUpdates[billId].originalData;
          delete state.pendingUpdates[billId];
          state.calculations = calculateBillsState(state.items);
        }
        state.error = action.error.message || 'Failed to update bill';
      });
  }
});

export const {
  setBills,
  addBill,
  updateBill,
  setSelectedBillId,
  updateBillSplits,
  updatePaymentStatus,
  setFilters,
  setLoading,
  setError,
  recalculateState
} = billsSlice.actions;

export default billsSlice.reducer;

// Basic Selectors
export const selectBillsItems = (state: { bills: BillsState }) => state.bills.items;
export const selectBillsList = (state: { bills: BillsState }) => Object.values(state.bills.items);
export const selectSelectedBillId = (state: { bills: BillsState }) => state.bills.selectedBillId;
export const selectLoading = (state: { bills: BillsState }) => state.bills.loading;
export const selectError = (state: { bills: BillsState }) => state.bills.error;
export const selectFilters = (state: { bills: BillsState }) => state.bills.filters;
export const selectCalculations = (state: { bills: BillsState }) => state.bills.calculations;
export const selectLastUpdated = (state: { bills: BillsState }) => state.bills.lastUpdated;

// Memoized Selectors
export const selectSelectedBill = createSelector(
  [selectBillsItems, selectSelectedBillId],
  (items, selectedId) => selectedId ? items[selectedId] : null
);

export const selectBillById = createSelector(
  [selectBillsItems, (_state: { bills: BillsState }, id: number) => id],
  (items, id) => items[id]
);

export const selectFilteredBills = createSelector(
  [selectBillsList, selectFilters],
  (bills, filters) => {
    return bills.filter(bill => {
      if (filters.status && bill.status !== filters.status) return false;
      if (filters.month && bill.month !== filters.month) return false;
      if (filters.accountId !== undefined) {
        const isMainAccount = bill.account_id === filters.accountId;
        const hasSplitForAccount = bill.splits?.some(split => split.account_id === filters.accountId);
        if (!isMainAccount && !hasSplitForAccount) return false;
      }
      if (filters.dateRange) {
        const billDate = new Date(bill.due_date!);
        const startDate = new Date(filters.dateRange.start_date);
        const endDate = new Date(filters.dateRange.end_date);
        if (billDate < startDate || billDate > endDate) return false;
      }
      if (filters.searchTerm) {
        const searchLower = filters.searchTerm.toLowerCase();
        return (
          bill.bill_name.toLowerCase().includes(searchLower) ||
          bill.account_name?.toLowerCase().includes(searchLower)
        );
      }
      return true;
    });
  }
);

export const selectBillsByAccount = createSelector(
  [selectBillsList, (_state: { bills: BillsState }, accountId: number) => accountId],
  (bills, accountId) => bills.filter(bill => {
    const isMainAccount = bill.account_id === accountId;
    const hasSplitForAccount = bill.splits?.some(split => split.account_id === accountId);
    return isMainAccount || hasSplitForAccount;
  })
);

export const selectUnpaidBills = createSelector(
  [selectBillsList],
  (bills) => bills.filter(bill => !bill.paid)
);

export const selectOverdueBills = createSelector(
  [selectBillsList],
  (bills) => bills.filter(bill => bill.daysOverdue > 0)
);

export const selectUpcomingBills = createSelector(
  [selectBillsList],
  (bills) => bills.filter(bill => !bill.paid && bill.daysOverdue <= 0)
);

// Pending Updates Selectors
export const selectPendingUpdates = (state: { bills: BillsState }) => state.bills.pendingUpdates;

export const selectHasPendingUpdate = createSelector(
  [selectPendingUpdates, (_state: { bills: BillsState }, billId: number) => billId],
  (pendingUpdates, billId) => !!pendingUpdates[billId]
);

export const selectPendingUpdateType = createSelector(
  [selectPendingUpdates, (_state: { bills: BillsState }, billId: number) => billId],
  (pendingUpdates, billId) => pendingUpdates[billId]?.type
);

export const selectPendingUpdateTimestamp = createSelector(
  [selectPendingUpdates, (_state: { bills: BillsState }, billId: number) => billId],
  (pendingUpdates, billId) => pendingUpdates[billId]?.timestamp
);

export const selectOriginalBillData = createSelector(
  [selectPendingUpdates, (_state: { bills: BillsState }, billId: number) => billId],
  (pendingUpdates, billId) => pendingUpdates[billId]?.originalData
);

// Optimistic State Selectors
export const selectOptimisticCalculations = createSelector(
  [selectCalculations, selectPendingUpdates],
  (calculations, pendingUpdates) => {
    // If there are no pending updates, return the current calculations
    if (Object.keys(pendingUpdates).length === 0) {
      return calculations;
    }

    // Clone the calculations to avoid mutating the state
    return {
      ...calculations,
      lastUpdated: new Date().toISOString(),
      // Add a flag to indicate these are optimistic calculations
      isOptimistic: true
    };
  }
);

export const selectHasOptimisticUpdates = createSelector(
  [selectPendingUpdates],
  (pendingUpdates) => Object.keys(pendingUpdates).length > 0
);
