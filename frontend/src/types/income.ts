export interface Income {
  id: number;
  date: string;
  source: string;
  amount: number;
  deposited: boolean;
  account_id?: number;
  undeposited_amount?: number;
}

export type IncomeCreate = Omit<Income, 'id'>;

export type IncomeUpdate = Partial<IncomeCreate>;
