export type BillStatus = 'paid' | 'unpaid' | 'overdue';

export interface BillSplit {
  id?: number;
  bill_id?: number;
  account_id: number;
  amount: number;
  created_at?: string;
  updated_at?: string;
}

export interface Bill {
  id?: number;
  month: string;
  day_of_month: number;
  due_date?: string;
  paid_date?: string;
  bill_name: string;
  amount: number;
  account_id: number;
  account_name?: string;
  auto_pay: boolean;
  paid?: boolean;
  up_to_date?: boolean;
  splits?: BillSplit[];
}

export interface BillDateRange {
  start_date: string;
  end_date: string;
}

export interface BillTableRow extends Bill {
  status: BillStatus;
  daysOverdue: number;
  splitAmounts?: { [accountId: number]: number };
}

export interface BillCalculations {
  totalAmount: number;
  totalUnpaid: number;
  totalByAccount: { [accountId: number]: number };
  totalByStatus: { [key in BillStatus]: number };
  upcomingBills: number;
  overdueBills: number;
  lastUpdated: string;
}

export interface BillFilters {
  status?: BillStatus;
  month?: string;
  accountId?: number;
  dateRange?: BillDateRange;
  searchTerm?: string;
}

export interface BillUpdatePayload {
  id: number;
  updates: Partial<Bill>;
}

export interface BillSplitUpdatePayload {
  billId: number;
  splits: BillSplit[];
}

export interface BillPaymentUpdatePayload {
  billId: number;
  paid: boolean;
  paidDate?: string;
}
