import { Decimal } from 'decimal.js';

export type AccountType = 'credit' | 'checking' | 'savings';

export interface Account {
  id: number;
  name: string;
  type: AccountType;
  available_balance: Decimal;
  available_credit: Decimal | null;
  total_limit: Decimal | null;
  last_statement_balance: Decimal | null;
  last_statement_date: Date | null;
  created_at: Date;
  updated_at: Date;
}

export interface AccountCreate {
  name: string;
  type: AccountType;
  available_balance: Decimal;
  available_credit?: Decimal;
  total_limit?: Decimal;
  last_statement_balance?: Decimal;
  last_statement_date?: Date;
}

export interface AccountUpdate {
  name?: string;
  type?: AccountType;
  available_balance?: Decimal;
  available_credit?: Decimal;
  total_limit?: Decimal;
  last_statement_balance?: Decimal;
  last_statement_date?: Date;
}
