import { Account, AccountCreate, AccountUpdate, AccountType } from '../types/accounts';
import { Decimal } from 'decimal.js';

const BASE_URL = '/api/v1/accounts';

interface RawAccount {
  id: number;
  name: string;
  type: AccountType;
  available_balance: string;
  available_credit: string | null;
  total_limit: string | null;
  last_statement_balance: string | null;
  last_statement_date: string | null;
  created_at: string;
  updated_at: string;
}

const mapRawAccount = (data: RawAccount): Account => ({
  ...data,
  available_balance: new Decimal(data.available_balance),
  available_credit: data.available_credit ? new Decimal(data.available_credit) : null,
  total_limit: data.total_limit ? new Decimal(data.total_limit) : null,
  last_statement_balance: data.last_statement_balance ? new Decimal(data.last_statement_balance) : null,
  last_statement_date: data.last_statement_date ? new Date(data.last_statement_date) : null,
  created_at: new Date(data.created_at),
  updated_at: new Date(data.updated_at),
});

export const getAccounts = async (): Promise<Account[]> => {
  const response = await fetch(BASE_URL);
  if (!response.ok) {
    throw new Error('Failed to fetch accounts');
  }
  const data = await response.json();
  return data.map(mapRawAccount);
};

export const createAccount = async (account: AccountCreate): Promise<Account> => {
  const response = await fetch(BASE_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(account),
  });
  if (!response.ok) {
    throw new Error('Failed to create account');
  }
  const data = await response.json();
  return mapRawAccount(data);
};

export const updateAccount = async (id: number, account: AccountUpdate): Promise<Account> => {
  const response = await fetch(`${BASE_URL}/${id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(account),
  });
  if (!response.ok) {
    throw new Error('Failed to update account');
  }
  const data = await response.json();
  return mapRawAccount(data);
};

export const deleteAccount = async (id: number): Promise<void> => {
  const response = await fetch(`${BASE_URL}/${id}`, {
    method: 'DELETE',
  });
  if (!response.ok) {
    throw new Error('Failed to delete account');
  }
};
