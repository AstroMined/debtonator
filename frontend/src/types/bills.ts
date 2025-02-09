export interface Bill {
  id: number;
  month: string;
  dayOfMonth: number;
  dueDate: string;
  paidDate?: string;
  billName: string;
  amount: number;
  upToDate: boolean;
  account: string;
  autoPay: boolean;
  paid: boolean;
  amexAmount?: number;
  unlimitedAmount?: number;
  ufcuAmount?: number;
}

export type BillStatus = 'paid' | 'unpaid' | 'overdue';

export interface BillTableRow extends Bill {
  status: BillStatus;
}

export type Account = 'AMEX' | 'UNLIMITED' | 'UFCU';

export interface BillUpdatePayload {
  id: number;
  paid: boolean;
  paidDate?: string;
}
