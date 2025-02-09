import { Decimal } from 'decimal.js';

export const formatCurrency = (amount: Decimal | number | null): string => {
  if (amount === null) return '-';
  
  const formatter = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });

  return formatter.format(typeof amount === 'number' ? amount : amount.toNumber());
};

export const parseCurrency = (value: string): Decimal | null => {
  if (!value) return null;
  
  // Remove currency symbol, commas, and other non-numeric characters except decimal point and minus sign
  const cleanValue = value.replace(/[^0-9.-]/g, '');
  
  if (!cleanValue || isNaN(Number(cleanValue))) {
    return null;
  }
  
  return new Decimal(cleanValue);
};
