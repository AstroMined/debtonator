import axios from 'axios';

export interface Account {
  id: number;
  name: string;
  type: string;
  available_balance: number;
  available_credit?: number;
  total_limit?: number;
  last_statement_balance?: number;
  last_statement_date?: string;
}

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const getAccounts = async (): Promise<Account[]> => {
  const response = await axios.get(`${BASE_URL}/v1/accounts`);
  return response.data;
};

export const getAccount = async (id: number): Promise<Account> => {
  const response = await axios.get(`${BASE_URL}/v1/accounts/${id}`);
  return response.data;
};

export const createAccount = async (account: Omit<Account, 'id'>): Promise<Account> => {
  const response = await axios.post(`${BASE_URL}/v1/accounts`, account);
  return response.data;
};

export const updateAccount = async (id: number, account: Partial<Account>): Promise<Account> => {
  const response = await axios.put(`${BASE_URL}/v1/accounts/${id}`, account);
  return response.data;
};

export const deleteAccount = async (id: number): Promise<void> => {
  await axios.delete(`${BASE_URL}/v1/accounts/${id}`);
};
