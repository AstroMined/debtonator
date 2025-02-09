import { Income } from '../types/income';

const API_BASE_URL = '/api/v1';

export const getIncomes = async (): Promise<Income[]> => {
  const response = await fetch(`${API_BASE_URL}/income`);
  if (!response.ok) {
    throw new Error('Failed to fetch incomes');
  }
  return response.json();
};

export const createIncome = async (income: Income): Promise<Income> => {
  const response = await fetch(`${API_BASE_URL}/income`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(income),
  });
  if (!response.ok) {
    throw new Error('Failed to create income');
  }
  return response.json();
};

export const updateIncome = async (id: number, income: Income): Promise<Income> => {
  const response = await fetch(`${API_BASE_URL}/income/${id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(income),
  });
  if (!response.ok) {
    throw new Error('Failed to update income');
  }
  return response.json();
};

export const deleteIncome = async (id: number): Promise<void> => {
  const response = await fetch(`${API_BASE_URL}/income/${id}`, {
    method: 'DELETE',
  });
  if (!response.ok) {
    throw new Error('Failed to delete income');
  }
};
