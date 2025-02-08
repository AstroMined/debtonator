# Product Context: Debtonator

## Problem Statement
Managing bills and cashflow using Excel is cumbersome and requires manual updates. The current system, while functional, requires significant effort to maintain and isn't easily accessible across devices.

## Current Solution
The existing Excel solution consists of three main components:

### Bills Sheet
- Historical record of all bills since 2017
- Tracks payment status and account allocation
- Manages recurring and one-time bills
- Columns:
  - Month
  - Day of Month
  - Due Date
  - Paid Date
  - Bill Name
  - Amount
  - Up To Date?
  - Account
  - Auto Pay?
  - Paid?
  - Account-specific columns (AMEX, Unlimited, UFCU)

### Income Sheet
- Tracks all income sources
- Manages deposit status
- Columns:
  - Date
  - Income Source
  - Amount
  - Deposited?
  - Income (calculated field for undeposited amounts)

### Cashflow Sheet
- Provides financial forecasting
- Tracks account balances
- Calculates required additional income
- Special calculations:
  - Available credit/balance tracking
  - Period-based minimum calculations
  - Income requirements at various work hours
  - Tax consideration in calculations (80% of gross needed)

## User Experience Goals

### Immediate Access
- Quick view of current financial status
- Easy access to upcoming bills
- Clear indication of required actions

### Simplified Data Entry
- Streamlined bill entry process
- Quick payment status updates
- Automated recurring bill creation

### Clear Visualization
- Visual representation of cashflow
- Clear forecasting views
- Account balance tracking

### Mobile Access
- Access financial data on the go
- Quick bill payment status updates
- Real-time financial position checking

## Key Differentiators
1. Maintains existing complex calculations while simplifying interface
2. Preserves historical data while enabling better future tracking
3. Enables multi-device access while maintaining data integrity
4. Provides foundation for future automation and banking integration
