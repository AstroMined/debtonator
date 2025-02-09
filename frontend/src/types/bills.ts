export interface BillSplit {
  id?: number;
  bill_id?: number;
  account_id: number;
  amount: number;
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
