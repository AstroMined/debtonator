export interface Income {
  id?: number;
  date: string;
  source: string;
  amount: number;
  deposited: boolean;
  target_account_id: number;
  target_account_name?: string;
  undeposited_amount?: number;
}

export interface IncomeTableRow extends Income {
  formattedDate: string;
}
