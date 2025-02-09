import { Income } from '../types/income';

interface ImportError {
  row: number;
  field: string;
  message: string;
}

interface ImportPreview {
  records: Array<Omit<Income, 'id'>>;
  validation_errors: ImportError[];
  total_records: number;
}

interface ImportResponse {
  success: boolean;
  processed: number;
  succeeded: number;
  failed: number;
  errors?: ImportError[];
}

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

export const updateIncome = async (id: number, income: Partial<Income>): Promise<Income> => {
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

export const previewIncomeImport = async (file: File): Promise<ImportPreview> => {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/bulk-import/income/preview`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error previewing income import:', error);
    throw error;
  }
};

export const importIncome = async (file: File): Promise<ImportResponse> => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('preview', 'false');

    const response = await fetch(`${API_BASE_URL}/bulk-import/income`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error importing income:', error);
    throw error;
  }
};
