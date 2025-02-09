import { Bill, BillDateRange } from '../types/bills';

interface ImportError {
  row: number;
  field: string;
  message: string;
}

interface ImportPreview {
  records: Array<Omit<Bill, 'id'>>;
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

export const getBills = async (dateRange?: BillDateRange): Promise<Bill[]> => {
  try {
    const queryParams = dateRange 
      ? `?start_date=${dateRange.start_date}&end_date=${dateRange.end_date}`
      : '';
    const response = await fetch(`${API_BASE_URL}/bills${queryParams}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching bills:', error);
    throw error;
  }
};

export const getBill = async (id: number): Promise<Bill> => {
  try {
    const response = await fetch(`${API_BASE_URL}/bills/${id}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching bill:', error);
    throw error;
  }
};

export const createBill = async (bill: Omit<Bill, 'id'>): Promise<Bill> => {
  try {
    const response = await fetch(`${API_BASE_URL}/bills`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(bill),
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error creating bill:', error);
    throw error;
  }
};

export const updateBill = async (id: number, bill: Partial<Bill>): Promise<Bill> => {
  try {
    const response = await fetch(`${API_BASE_URL}/bills/${id}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(bill),
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error updating bill:', error);
    throw error;
  }
};

export const deleteBill = async (id: number): Promise<void> => {
  try {
    const response = await fetch(`${API_BASE_URL}/bills/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
  } catch (error) {
    console.error('Error deleting bill:', error);
    throw error;
  }
};

export const previewBillsImport = async (file: File): Promise<ImportPreview> => {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/bulk-import/bills/preview`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error previewing bills import:', error);
    throw error;
  }
};

export const importBills = async (file: File): Promise<ImportResponse> => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('preview', 'false');

    const response = await fetch(`${API_BASE_URL}/bulk-import/bills`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error importing bills:', error);
    throw error;
  }
};

export const updateBillPaymentStatus = async (id: number, paid: boolean): Promise<Bill> => {
  try {
    const response = await fetch(`${API_BASE_URL}/bills/${id}/payment-status`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ paid }),
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error updating bill payment status:', error);
    throw error;
  }
};
