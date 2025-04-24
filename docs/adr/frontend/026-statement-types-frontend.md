# ADR-026: Statement Types Frontend

## Status

Proposed

## Executive Summary

This ADR defines the frontend implementation for the polymorphic statement history structure established in ADR-025. We will create a comprehensive component architecture that renders type-specific information for different statement types through a component registry pattern. This includes specialized visualizations, interaction patterns, and responsive UI components for credit, checking, savings, and other statement types. The implementation integrates with the feature flag system for controlled rollout, follows accessibility best practices, and provides an extensible foundation for future statement types while maintaining consistent user experience across all statement types.

## Context

Following ADR-025, which introduced a polymorphic statement history structure in the backend, we need to enhance the frontend to properly display and interact with these different statement types. Each statement type (credit, checking, savings, etc.) has unique data and user interaction patterns that should be reflected in the UI.

The current frontend implementation has several limitations:

1. All statements are displayed with the same UI component regardless of type
2. Credit-specific fields (minimum_payment, due_date) are shown for all statement types
3. The UI doesn't leverage type-specific data for enhanced visualization
4. There's no specialized interaction patterns for different statement types
5. The statement list and detail views lack proper type-specific filtering and organization

## Decision

We will implement a comprehensive frontend architecture for statement types that will:

1. Create type-specific UI components for different statement types
2. Implement a component registry pattern for dynamic component loading
3. Enhance visualization with type-specific charts and metrics
4. Provide specialized interaction patterns for each statement type
5. Integrate with the feature flag system for controlled rollout

### Statement Type Component Architecture

We will implement a component hierarchy for statement types:

```tree
src/
  components/
    statements/
      base/
        StatementCard.tsx         # Base component for all statement types
        StatementDetail.tsx       # Base detail view component
        StatementList.tsx         # Statement list component with type filtering
      types/
        credit/
          CreditStatementCard.tsx     # Credit-specific card component
          CreditStatementDetail.tsx   # Credit-specific detail view
          CreditPaymentForm.tsx       # Payment form for credit statements
          CreditStatementChart.tsx    # Specialized visualization for credit
        checking/
          CheckingStatementCard.tsx   # Checking-specific card component
          CheckingStatementDetail.tsx # Checking-specific detail view
          TransactionList.tsx         # Transaction list for checking statements
          ActivityChart.tsx           # Activity visualization for checking
        savings/
          SavingsStatementCard.tsx    # Savings-specific card component
          SavingsStatementDetail.tsx  # Savings-specific detail view
          InterestChart.tsx           # Interest visualization for savings
      index.ts                    # Exports all components with registry
```

### Component Registry Pattern

To dynamically load the appropriate component for each statement type:

```typescript
// src/components/statements/registry.ts
import React from 'react';
import { StatementCard as BaseStatementCard } from './base/StatementCard';
import { StatementDetail as BaseStatementDetail } from './base/StatementDetail';
import { CreditStatementCard } from './types/credit/CreditStatementCard';
import { CreditStatementDetail } from './types/credit/CreditStatementDetail';
import { CheckingStatementCard } from './types/checking/CheckingStatementCard';
import { CheckingStatementDetail } from './types/checking/CheckingStatementDetail';
import { SavingsStatementCard } from './types/savings/SavingsStatementCard';
import { SavingsStatementDetail } from './types/savings/SavingsStatementDetail';
import { FeatureFlagService } from '../../services/feature-flags';

interface ComponentRegistry {
  [key: string]: {
    card: React.ComponentType<any>;
    detail: React.ComponentType<any>;
    featureFlag?: string;
  };
}

// Registry of statement type components
export const statementComponentRegistry: ComponentRegistry = {
  credit: {
    card: CreditStatementCard,
    detail: CreditStatementDetail,
    featureFlag: 'BANKING_ACCOUNT_TYPES_ENABLED'
  },
  checking: {
    card: CheckingStatementCard,
    detail: CheckingStatementDetail,
    featureFlag: 'BANKING_ACCOUNT_TYPES_ENABLED'
  },
  savings: {
    card: SavingsStatementCard,
    detail: SavingsStatementDetail,
    featureFlag: 'BANKING_ACCOUNT_TYPES_ENABLED'
  },
  // Add more statement types as they are implemented
};

// Function to get the appropriate component for a statement type
export function getStatementComponent(
  type: string, 
  componentType: 'card' | 'detail',
  featureFlagService: FeatureFlagService
): React.ComponentType<any> {
  const registry = statementComponentRegistry[type];
  
  // If type is not in registry or feature flag is disabled, return base component
  if (!registry || (registry.featureFlag && !featureFlagService.isEnabled(registry.featureFlag))) {
    return componentType === 'card' ? BaseStatementCard : BaseStatementDetail;
  }
  
  return registry[componentType];
}
```

### Dynamic Statement Rendering

To render the appropriate component based on statement type:

```typescript
// src/components/statements/StatementRenderer.tsx
import React from 'react';
import { useFeatureFlagService } from '../../hooks/useFeatureFlagService';
import { getStatementComponent } from './registry';

interface StatementRendererProps {
  statement: any;
  type: 'card' | 'detail';
}

export const StatementRenderer: React.FC<StatementRendererProps> = ({
  statement,
  type
}) => {
  const featureFlagService = useFeatureFlagService();
  const StatementComponent = getStatementComponent(
    statement.statement_type,
    type,
    featureFlagService
  );
  
  return <StatementComponent statement={statement} />;
};
```

### Type-Specific Visualizations

Each statement type will have specialized visualizations:

#### Credit Statement Visualization

```typescript
// src/components/statements/types/credit/CreditStatementChart.tsx
import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

interface CreditStatementChartProps {
  statement: any;
  previousStatements?: any[];
}

export const CreditStatementChart: React.FC<CreditStatementChartProps> = ({
  statement,
  previousStatements = []
}) => {
  // Combine current and previous statements for trending
  const allStatements = [...previousStatements, statement].slice(-6);
  
  // Prepare data for chart
  const data = allStatements.map(stmt => ({
    date: new Date(stmt.statement_date).toLocaleDateString(),
    balance: stmt.statement_balance,
    minimum: stmt.minimum_payment || 0,
    interest: stmt.interest_charged || 0,
    fees: stmt.fees_charged || 0
  }));
  
  return (
    <div className="p-4 bg-white rounded-lg shadow">
      <h3 className="text-lg font-medium mb-4">Statement History</h3>
      <BarChart width={600} height={300} data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Bar dataKey="balance" fill="#8884d8" name="Statement Balance" />
        <Bar dataKey="minimum" fill="#82ca9d" name="Minimum Payment" />
        <Bar dataKey="interest" fill="#ffc658" name="Interest Charged" />
        <Bar dataKey="fees" fill="#ff8042" name="Fees" />
      </BarChart>
    </div>
  );
};
```

#### Checking Statement Visualization

```typescript
// src/components/statements/types/checking/ActivityChart.tsx
import React from 'react';
import { PieChart, Pie, Cell, Legend, Tooltip } from 'recharts';

interface ActivityChartProps {
  statement: any;
}

export const ActivityChart: React.FC<ActivityChartProps> = ({
  statement
}) => {
  // Prepare data for pie chart
  const data = [
    { name: 'Deposits', value: statement.deposits_total || 0 },
    { name: 'Withdrawals', value: statement.withdrawals_total || 0 },
    { name: 'Fees', value: statement.fees_charged || 0 }
  ];
  
  const COLORS = ['#0088FE', '#FF8042', '#FFBB28'];
  
  return (
    <div className="p-4 bg-white rounded-lg shadow">
      <h3 className="text-lg font-medium mb-4">Activity Breakdown</h3>
      <div className="flex items-center justify-between">
        <div>
          <div className="mb-2">
            <span className="font-medium">Deposits: </span>
            <span>{statement.deposits_count || 0} transactions</span>
          </div>
          <div className="mb-2">
            <span className="font-medium">Withdrawals: </span>
            <span>{statement.withdrawals_count || 0} transactions</span>
          </div>
          <div className="mb-2">
            <span className="font-medium">Fees: </span>
            <span>${statement.fees_charged || 0}</span>
          </div>
        </div>
        <PieChart width={200} height={200}>
          <Pie
            data={data}
            cx={100}
            cy={100}
            innerRadius={60}
            outerRadius={80}
            paddingAngle={5}
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </div>
    </div>
  );
};
```

### Type-Specific User Interactions

Different statement types require different user interactions:

#### Credit Statement Payment Component

```typescript
// src/components/statements/types/credit/CreditPaymentForm.tsx
import React, { useState } from 'react';
import { usePaymentService } from '../../../../hooks/usePaymentService';

interface CreditPaymentFormProps {
  statement: any;
  onSuccess?: () => void;
}

export const CreditPaymentForm: React.FC<CreditPaymentFormProps> = ({
  statement,
  onSuccess
}) => {
  const [paymentAmount, setPaymentAmount] = useState<string>(
    statement.minimum_payment?.toString() || '0'
  );
  const [paymentDate, setPaymentDate] = useState<string>(
    new Date().toISOString().split('T')[0]
  );
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  
  const paymentService = usePaymentService();
  
  const handlePaymentSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      await paymentService.makePayment({
        statementId: statement.id,
        amount: parseFloat(paymentAmount),
        paymentDate,
        accountId: statement.account_id
      });
      
      if (onSuccess) {
        onSuccess();
      }
    } catch (err) {
      setError(err.message || 'Failed to make payment');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="p-4 bg-white rounded-lg shadow">
      <h3 className="text-lg font-medium mb-4">Make a Payment</h3>
      
      {error && (
        <div className="mb-4 p-2 bg-red-100 text-red-700 rounded">
          {error}
        </div>
      )}
      
      <form onSubmit={handlePaymentSubmit}>
        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">
            Payment Amount
          </label>
          <div className="flex items-center">
            <button
              type="button"
              className="px-3 py-2 bg-gray-200 hover:bg-gray-300 rounded-l"
              onClick={() => setPaymentAmount(statement.minimum_payment?.toString() || '0')}
            >
              Minimum
            </button>
            <button
              type="button"
              className="px-3 py-2 bg-gray-200 hover:bg-gray-300"
              onClick={() => setPaymentAmount(statement.statement_balance?.toString() || '0')}
            >
              Full Balance
            </button>
            <div className="relative flex-1">
              <span className="absolute left-3 top-2">$</span>
              <input
                type="number"
                value={paymentAmount}
                onChange={(e) => setPaymentAmount(e.target.value)}
                className="pl-6 pr-3 py-2 w-full border rounded-r"
                step="0.01"
                min="0"
                max={statement.statement_balance}
              />
            </div>
          </div>
        </div>
        
        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">
            Payment Date
          </label>
          <input
            type="date"
            value={paymentDate}
            onChange={(e) => setPaymentDate(e.target.value)}
            className="px-3 py-2 w-full border rounded"
            min={new Date().toISOString().split('T')[0]}
            max={statement.payment_due_date?.split('T')[0]}
          />
        </div>
        
        <button
          type="submit"
          className="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white rounded"
          disabled={loading}
        >
          {loading ? 'Processing...' : 'Submit Payment'}
        </button>
      </form>
    </div>
  );
};
```

#### Savings Statement Interest Calculator

```typescript
// src/components/statements/types/savings/InterestCalculator.tsx
import React, { useState, useEffect } from 'react';

interface InterestCalculatorProps {
  statement: any;
}

export const InterestCalculator: React.FC<InterestCalculatorProps> = ({
  statement
}) => {
  const [additionalDeposit, setAdditionalDeposit] = useState<string>('100');
  const [months, setMonths] = useState<string>('12');
  const [projectedInterest, setProjectedInterest] = useState<number>(0);
  
  // Calculate projected interest based on current APY and additional deposits
  useEffect(() => {
    const calculate = () => {
      const currentBalance = statement.statement_balance || 0;
      const apy = statement.apy_for_period || 0;
      const deposit = parseFloat(additionalDeposit) || 0;
      const periodMonths = parseInt(months) || 0;
      
      // Monthly interest rate
      const monthlyRate = apy / 100 / 12;
      
      // Future value calculation with monthly contributions
      let futureValue = currentBalance;
      for (let i = 0; i < periodMonths; i++) {
        futureValue = futureValue * (1 + monthlyRate) + deposit;
      }
      
      const totalInterest = futureValue - currentBalance - (deposit * periodMonths);
      setProjectedInterest(parseFloat(totalInterest.toFixed(2)));
    };
    
    calculate();
  }, [statement, additionalDeposit, months]);
  
  return (
    <div className="p-4 bg-white rounded-lg shadow">
      <h3 className="text-lg font-medium mb-4">Interest Calculator</h3>
      
      <div className="mb-4">
        <label className="block text-sm font-medium mb-1">
          Current APY
        </label>
        <div className="px-3 py-2 border rounded bg-gray-50">
          {(statement.apy_for_period || 0).toFixed(2)}%
        </div>
      </div>
      
      <div className="mb-4">
        <label className="block text-sm font-medium mb-1">
          Monthly Deposit
        </label>
        <div className="relative">
          <span className="absolute left-3 top-2">$</span>
          <input
            type="number"
            value={additionalDeposit}
            onChange={(e) => setAdditionalDeposit(e.target.value)}
            className="pl-6 pr-3 py-2 w-full border rounded"
            step="10"
            min="0"
          />
        </div>
      </div>
      
      <div className="mb-4">
        <label className="block text-sm font-medium mb-1">
          Time Period (months)
        </label>
        <input
          type="number"
          value={months}
          onChange={(e) => setMonths(e.target.value)}
          className="px-3 py-2 w-full border rounded"
          step="1"
          min="1"
          max="120"
        />
      </div>
      
      <div className="mt-6 p-3 bg-blue-50 rounded-lg">
        <h4 className="font-medium text-blue-800">Projected Interest</h4>
        <p className="text-2xl font-bold text-blue-600">${projectedInterest}</p>
        <p className="text-sm text-blue-700">
          over {months} months with ${additionalDeposit}/month additional deposits
        </p>
      </div>
    </div>
  );
};
```

### Statement List with Type Filtering

A unified statement list view with type-specific filtering:

```typescript
// src/components/statements/StatementListView.tsx
import React, { useState, useEffect } from 'react';
import { useStatementService } from '../../hooks/useStatementService';
import { useFeatureFlagService } from '../../hooks/useFeatureFlagService';
import { StatementRenderer } from './StatementRenderer';

interface StatementListViewProps {
  accountId?: number; // Optional - filter by account
}

export const StatementListView: React.FC<StatementListViewProps> = ({
  accountId
}) => {
  const [statements, setStatements] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [typeFilter, setTypeFilter] = useState<string>('all');
  
  const statementService = useStatementService();
  const featureFlagService = useFeatureFlagService();
  
  // Get available statement types based on feature flags
  const availableTypes = [
    { id: 'all', name: 'All Types' },
    ...(featureFlagService.isEnabled('BANKING_ACCOUNT_TYPES_ENABLED') 
      ? [
          { id: 'credit', name: 'Credit' },
          { id: 'checking', name: 'Checking' },
          { id: 'savings', name: 'Savings' }
        ] 
      : []),
    ...(featureFlagService.isEnabled('STATEMENT_TYPE_LOAN_ENABLED') 
      ? [{ id: 'loan', name: 'Loan' }] 
      : [])
  ];
  
  useEffect(() => {
    const fetchStatements = async () => {
      setLoading(true);
      setError(null);
      
      try {
        let result;
        if (accountId) {
          result = await statementService.getStatementsByAccount(accountId);
        } else {
          result = await statementService.getAllStatements();
        }
        
        setStatements(result);
      } catch (err) {
        setError(err.message || 'Failed to fetch statements');
      } finally {
        setLoading(false);
      }
    };
    
    fetchStatements();
  }, [accountId, statementService]);
  
  // Filter statements by type
  const filteredStatements = typeFilter === 'all'
    ? statements
    : statements.filter(s => s.statement_type === typeFilter);
  
  return (
    <div className="space-y-4">
      <div className="flex space-x-2 overflow-x-auto pb-2">
        {availableTypes.map(type => (
          <button
            key={type.id}
            className={`px-4 py-2 rounded-full ${
              typeFilter === type.id
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 hover:bg-gray-300'
            }`}
            onClick={() => setTypeFilter(type.id)}
          >
            {type.name}
          </button>
        ))}
      </div>
      
      {loading ? (
        <div className="p-4 text-center">Loading statements...</div>
      ) : error ? (
        <div className="p-4 text-red-600">{error}</div>
      ) : filteredStatements.length === 0 ? (
        <div className="p-4 text-center">No statements found</div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {filteredStatements.map(statement => (
            <StatementRenderer
              key={statement.id}
              statement={statement}
              type="card"
            />
          ))}
        </div>
      )}
    </div>
  );
};
```

## Responsive Design Approach

All statement components will be designed with a mobile-first approach:

```typescript
// src/components/statements/types/credit/CreditStatementCard.tsx
import React from 'react';
import { formatCurrency } from '../../../../utils/formatters';

interface CreditStatementCardProps {
  statement: any;
  compact?: boolean;
}

export const CreditStatementCard: React.FC<CreditStatementCardProps> = ({
  statement,
  compact = false
}) => {
  const isPaid = statement.is_paid;
  const isDueDate = statement.payment_due_date && new Date(statement.payment_due_date) > new Date();
  
  return (
    <div className={`rounded-lg shadow overflow-hidden ${
      isPaid ? 'bg-green-50 border border-green-200' : 
      isDueDate ? 'bg-yellow-50 border border-yellow-200' : 
      'bg-white border border-gray-200'
    }`}>
      <div className="p-4">
        <div className="flex justify-between items-start">
          <div>
            <h3 className="font-medium text-gray-900">
              {new Date(statement.statement_date).toLocaleDateString()}
            </h3>
            <p className="text-sm text-gray-500">
              Credit Statement
            </p>
          </div>
          <div className={`px-2 py-1 rounded text-xs font-medium ${
            isPaid ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'
          }`}>
            {isPaid ? 'Paid' : 'Unpaid'}
          </div>
        </div>
        
        <div className="mt-4 grid grid-cols-2 gap-x-4 gap-y-2">
          <div>
            <p className="text-xs text-gray-500">Statement Balance</p>
            <p className="font-semibold">
              {formatCurrency(statement.statement_balance)}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Minimum Payment</p>
            <p className="font-semibold">
              {formatCurrency(statement.minimum_payment || 0)}
            </p>
          </div>
          
          {!compact && (
            <>
              <div>
                <p className="text-xs text-gray-500">Interest Charged</p>
                <p className="font-semibold">
                  {formatCurrency(statement.interest_charged || 0)}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Fees Charged</p>
                <p className="font-semibold">
                  {formatCurrency(statement.fees_charged || 0)}
                </p>
              </div>
            </>
          )}
        </div>
        
        {statement.payment_due_date && (
          <div className={`mt-4 p-2 rounded text-sm ${
            isPaid ? 'bg-green-100 text-green-800' :
            new Date(statement.payment_due_date) < new Date() ? 
              'bg-red-100 text-red-800' : 
              'bg-yellow-100 text-yellow-800'
          }`}>
            {isPaid ? 'Paid on ' : 'Due date: '}
            {new Date(statement.payment_due_date).toLocaleDateString()}
          </div>
        )}
      </div>
      
      <div className="bg-gray-50 px-4 py-3 border-t border-gray-200">
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">
            Account: {statement.account?.name || `#${statement.account_id}`}
          </span>
          <button className="text-sm text-blue-600 hover:text-blue-800">
            View Details
          </button>
        </div>
      </div>
    </div>
  );
};
```

## Accessibility Requirements

All statement components will follow these accessibility requirements:

1. **Semantic HTML Structure**
   - Proper heading hierarchy (h1, h2, h3)
   - Appropriate ARIA roles and landmarks
   - Semantic table structure for tabular data

2. **Keyboard Accessibility**
   - All interactive elements must be keyboard accessible
   - Visual focus indicators for all interactive elements
   - Logical tab order through the interface

3. **Screen Reader Support**
   - Descriptive alt text for all images and charts
   - ARIA labels for interactive elements
   - Announcements for dynamic content changes

4. **Color Contrast**
   - Minimum 4.5:1 contrast ratio for normal text
   - Minimum 3:1 contrast ratio for large text
   - Color is not the only means of conveying information

Example implementation of accessible charts:

```typescript
// src/components/statements/types/checking/AccessibleActivityChart.tsx
import React from 'react';
import { PieChart, Pie, Cell, Legend, Tooltip } from 'recharts';

interface AccessibleActivityChartProps {
  statement: any;
}

export const AccessibleActivityChart: React.FC<AccessibleActivityChartProps> = ({
  statement
}) => {
  // Prepare data for pie chart
  const data = [
    { name: 'Deposits', value: statement.deposits_total || 0 },
    { name: 'Withdrawals', value: statement.withdrawals_total || 0 },
    { name: 'Fees', value: statement.fees_charged || 0 }
  ];
  
  const COLORS = ['#0088FE', '#FF8042', '#FFBB28'];
  
  // Generate data table for screen readers
  const dataTable = data.map(item => `${item.name}: $${item.value.toFixed(2)}`).join(', ');
  
  return (
    <div className="p-4 bg-white rounded-lg shadow" role="region" aria-label="Activity breakdown chart">
      <h3 className="text-lg font-medium mb-4" id="activity-chart-title">Activity Breakdown</h3>
      
      {/* Screen reader accessible summary */}
      <div className="sr-only">
        Statement activity breakdown: {dataTable}
      </div>
      
      <div className="flex items-center justify-between">
        <div>
          <div className="mb-2">
            <span className="font-medium">Deposits: </span>
            <span>${(statement.deposits_total || 0).toFixed(2)} ({statement.deposits_count || 0} transactions)</span>
          </div>
          <div className="mb-2">
            <span className="font-medium">Withdrawals: </span>
            <span>${(statement.withdrawals_total || 0).toFixed(2)} ({statement.withdrawals_count || 0} transactions)</span>
          </div>
          <div className="mb-2">
            <span className="font-medium">Fees: </span>
            <span>${(statement.fees_charged || 0).toFixed(2)}</span>
          </div>
        </div>
        
        {/* Accessible chart with appropriate ARIA attributes */}
        <div aria-hidden="true">
          <PieChart width={200} height={200}>
            <Pie
              data={data}
              cx={100}
              cy={100}
              innerRadius={60}
              outerRadius={80}
              paddingAngle={5}
              dataKey="value"
              aria-describedby="activity-chart-title"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </div>
      </div>
    </div>
  );
};
```

## User Flow for Statement Interaction

The user flow for interacting with statements will be:

1. **Statement List View**
   - User views all statements with type filtering
   - Statements are grouped by account or statement type
   - Visual indicators show status (paid/unpaid, due soon)
   - Type-specific card components show relevant information

2. **Statement Detail View**
   - User clicks on a statement card to view details
   - Type-specific detail component shows comprehensive information
   - Visual charts and metrics highlight key information
   - Action buttons for type-specific operations (make payment, etc.)

3. **Statement Actions**
   - Credit statements: Payment forms, payment history
   - Checking statements: Transaction lists, activity breakdown
   - Savings statements: Interest calculators, deposit/withdrawal history

## Performance Considerations

To ensure optimal frontend performance:

1. **Code Splitting**
   - Lazy load statement type components
   - Use dynamic imports for specialized visualizations
   - Separate chunks for different statement types

2. **Data Fetching Strategy**
   - Implement pagination for statement lists
   - Use caching for frequently accessed statements
   - Optimize API calls for statement detail views

3. **Rendering Optimization**
   - Virtualize long statement lists
   - Memoize expensive calculations
   - Optimize re-renders with React.memo and useMemo

## Implementation Plan

We recommend implementing this design in the following phases:

### Phase 1: Core Architecture

- [ ] Create base statement components (Card, Detail, List)
- [ ] Implement component registry pattern
- [ ] Set up feature flag integration
- [ ] Create statement renderer component

### Phase 2: Banking Statement Types

- [ ] Implement credit statement components
- [ ] Implement checking statement components
- [ ] Implement savings statement components
- [ ] Create specialized visualizations for each type

### Phase 3: Interactive Elements

- [ ] Implement credit payment form
- [ ] Create checking transaction list
- [ ] Build savings interest calculator
- [ ] Add type-specific actions and operations

### Phase 4: Polish and Accessibility

- [ ] Enhance responsive design for all components
- [ ] Implement comprehensive accessibility features
- [ ] Add animation and transitions
- [ ] Create comprehensive documentation

## Technical Details

### Architecture Overview

The statement types frontend implementation follows a component-based architecture using React with TypeScript, leveraging a registry pattern for dynamic component loading based on statement types. The approach ensures proper separation of concerns while maintaining consistent UI/UX across statement types through shared base components and type-specific implementations.

### Technology Stack

- **React with TypeScript**: Component-based UI with type safety
- **Redux Toolkit**: State management for statement data
- **Material-UI**: UI component library for consistent design
- **Recharts**: Data visualization for statement-specific charts
- **React Router**: Navigation between statement list and details
- **Feature Flag Integration**: Conditional feature availability

### Component Structure

```typescript
// Base statement component interface
interface StatementCardProps {
  statement: StatementDto;
  onClick?: (statementId: string) => void;
  compact?: boolean;
}

// Type-specific component implementation example
const CreditStatementCard: React.FC<StatementCardProps> = ({
  statement,
  onClick,
  compact = false
}) => {
  // Credit-specific implementation
};
```

The component architecture follows a hierarchical structure:

1. **Base Components**
   - `StatementCard`: Common card structure for all statement types
   - `StatementDetail`: Base detail view for all statement types
   - `StatementList`: List view with filtering capabilities

2. **Type-Specific Components**
   - Credit statement components (card, detail, payment form, charts)
   - Checking statement components (card, detail, transaction list, activity chart)
   - Savings statement components (card, detail, interest calculator, charts)

3. **Utility Components**
   - `StatementRenderer`: Dynamically selects appropriate component
   - `StatementTypeBadge`: Visual indicator of statement type
   - `StatementStatusBadge`: Visual indicator of payment status

### State Management

Statement data will be managed using Redux Toolkit with specialized selectors for different statement types:

```typescript
// src/store/slices/statements.slice.ts
import { createSlice, createAsyncThunk, createEntityAdapter } from '@reduxjs/toolkit';
import { createSelector } from 'reselect';
import { StatementDto } from '../../types/statement.types';
import { RootState } from '../store';
import { statementService } from '../../services/statement.service';

const statementsAdapter = createEntityAdapter<StatementDto>({
  selectId: (statement) => statement.id,
  sortComparer: (a, b) => 
    new Date(b.statement_date).getTime() - new Date(a.statement_date).getTime(),
});

const initialState = statementsAdapter.getInitialState({
  loading: false,
  error: null as string | null,
  filters: {
    type: 'all',
    dateRange: '3months',
    status: 'all',
  },
});

// Async thunks
export const fetchAllStatements = createAsyncThunk(
  'statements/fetchAll',
  async () => {
    return await statementService.getAllStatements();
  }
);

export const fetchStatementDetails = createAsyncThunk(
  'statements/fetchDetails',
  async (statementId: string) => {
    return await statementService.getStatementById(statementId);
  }
);

// Slice definition
const statementsSlice = createSlice({
  name: 'statements',
  initialState,
  reducers: {
    setFilter: (state, action) => {
      state.filters = { ...state.filters, ...action.payload };
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchAllStatements.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchAllStatements.fulfilled, (state, action) => {
        state.loading = false;
        statementsAdapter.setAll(state, action.payload);
      })
      .addCase(fetchAllStatements.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch statements';
      })
      .addCase(fetchStatementDetails.fulfilled, (state, action) => {
        statementsAdapter.upsertOne(state, action.payload);
      });
  },
});

// Selectors
export const { selectAll: selectAllStatements, selectById: selectStatementById } = 
  statementsAdapter.getSelectors<RootState>((state) => state.statements);

export const selectStatementsByType = createSelector(
  [selectAllStatements, (_, type: string) => type],
  (statements, type) => 
    type === 'all' ? statements : statements.filter(s => s.statement_type === type)
);

export const selectStatementsByStatus = createSelector(
  [selectAllStatements, (_, status: string) => status],
  (statements, status) => {
    if (status === 'all') return statements;
    if (status === 'paid') return statements.filter(s => s.is_paid);
    if (status === 'unpaid') return statements.filter(s => !s.is_paid);
    return statements;
  }
);

export const { setFilter } = statementsSlice.actions;
export default statementsSlice.reducer;
```

### API Integration

Statement data will be fetched and managed through specialized services that integrate with the backend API:

```typescript
// src/services/statement.service.ts
import { api } from './api';
import { StatementDto, StatementDetailDto } from '../types/statement.types';

export class StatementService {
  async getAllStatements(): Promise<StatementDto[]> {
    const response = await api.get('/api/statements');
    return response.data;
  }

  async getStatementById(id: string): Promise<StatementDetailDto> {
    const response = await api.get(`/api/statements/${id}`);
    return response.data;
  }

  async getStatementsByAccount(accountId: string): Promise<StatementDto[]> {
    const response = await api.get(`/api/accounts/${accountId}/statements`);
    return response.data;
  }

  async makePayment(paymentData: {
    statementId: string;
    amount: number;
    paymentDate: string;
    accountId: string;
  }): Promise<any> {
    const response = await api.post(`/api/statements/${paymentData.statementId}/payments`, paymentData);
    return response.data;
  }
}

export const statementService = new StatementService();
```

### Feature Flag Integration

Integration with the feature flag system ensures controlled rollout of statement type features:

```typescript
// src/hooks/useFeatureFlags.ts
import { useEffect, useState } from 'react';
import { FeatureFlagService } from '../services/feature-flags';

export function useFeatureFlags() {
  const [featureFlagService] = useState(() => new FeatureFlagService());
  const [initialized, setInitialized] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const initializeFlags = async () => {
      try {
        await featureFlagService.initialize();
        setInitialized(true);
      } catch (error) {
        setError('Failed to initialize feature flags');
      }
    };

    initializeFlags();
  }, [featureFlagService]);

  return {
    isEnabled: (flagName: string) => featureFlagService.isEnabled(flagName),
    initialized,
    error
  };
}
```

### Accessibility Features

All statement type components will implement comprehensive accessibility features:

1. **Semantic HTML Structure**
   - Proper heading hierarchy (h1-h6)
   - Appropriate ARIA landmarks (main, nav, complementary)
   - Semantic elements (section, article, header, footer)

2. **Keyboard Navigation**
   - All interactive elements are properly focusable
   - Custom keyboard shortcuts for common operations
   - Focus management when opening/closing modals
   - Focus trapping in modal dialogs

3. **Screen Reader Support**
   - Descriptive alt text for images and charts
   - Hidden descriptive text for complex charts
   - ARIA labels for interactive elements
   - Status announcements for dynamic content changes

4. **Color and Contrast**
   - Minimum 4.5:1 contrast ratio for all text
   - Status indications use both color and text/icons
   - High contrast mode support

### Security Considerations

1. **Authentication**
   - JWT-based authentication for all API calls
   - Token validation on sensitive operations

2. **Authorization**
   - Role-based access control for statement operations
   - Permission checks before sensitive actions (payments)

3. **Data Validation**
   - Client-side validation with Yup schemas
   - Server-side validation of all inputs
   - XSS prevention through React's built-in escaping

4. **Sensitive Data Handling**
   - No storage of sensitive financial data in local storage
   - Token storage in memory or secure cookie
   - Automatic session expiration after inactivity

## Consequences

### Positive

1. **Enhanced User Experience**: Users will see relevant information specific to each statement type, making it easier to understand their financial situation
2. **Improved Data Visualization**: Specialized charts and visualizations for each statement type provide better insights
3. **Streamlined Interactions**: Type-specific actions allow users to perform common tasks directly from statements
4. **Better Mobile Experience**: Responsive design patterns improve usability on smaller screens
5. **Future-Proof Architecture**: The component registry pattern makes it easy to add new statement types as they become available
6. **Consistent Design Language**: All statement types follow a unified design pattern while allowing for specialized content
7. **Accessibility Improvements**: Comprehensive accessibility features make the application usable by all users

### Negative

1. **Increased Component Complexity**: The specialized components increase the overall codebase size and complexity
2. **Development Time**: Creating specialized components for each statement type requires more initial development effort
3. **Maintenance Overhead**: More components to maintain and test with each update
4. **Bundle Size**: Additional components may increase the initial bundle size without proper code splitting
5. **Learning Curve**: New developers will need to understand the component registry pattern

### Neutral

1. **Feature Flag Dependencies**: Components depend on the feature flag system for conditional rendering
2. **API Dependencies**: Each statement type requires specific backend support
3. **Testing Requirements**: Need for both common and type-specific test cases
4. **Documentation Needs**: Requires clear documentation of the component registry pattern

## Quality Considerations

1. **Code Organization**: Clear directory structure separating base and type-specific components
2. **Component Testing**: Comprehensive unit tests for each statement component
3. **State Management**: Consistent use of Redux Toolkit for statement data
4. **UI Consistency**: Shared design patterns across all statement types
5. **Cross-Browser Compatibility**: Testing across all major browsers
6. **Error Handling**: Graceful fallbacks when specific statement data is missing
7. **Type Safety**: TypeScript interfaces for all statement types

## Performance and Resource Considerations

1. **Lazy Loading**: Code splitting to load statement type components on demand
2. **Bundle Size Impact**: ~2-5KB per statement type component (gzipped)
3. **Render Performance**:
   - List view: Capable of handling 100+ statements with virtualization
   - Detail view: Chart rendering optimized for 12-month history
4. **API Performance**:
   - Pagination for large statement histories
   - Caching of statement data
   - Optimistic UI updates for common actions
5. **Memory Usage**:
   - Redux store optimized for normalized statement data
   - Memoized selectors for derived data

## Development Considerations

1. **Development Effort**:
   - Core architecture: 2 weeks
   - Each statement type implementation: 1-2 weeks
   - Polish and accessibility: 1 week
   - Testing: 1-2 weeks throughout
   - Total: 6-8 weeks for initial implementation

2. **Technical Challenges**:
   - Ensuring consistent behavior across statement types
   - Managing feature flag integration
   - Handling edge cases in statement data
   - Ensuring proper accessibility for data visualizations

3. **Testing Requirements**:
   - Unit tests for all components
   - Integration tests for statement flows
   - Accessibility testing
   - Cross-browser compatibility
   - Mobile responsiveness

## Security and Compliance Considerations

1. **Data Protection**:
   - No caching of sensitive statement data
   - Secure handling of payment information
   - Proper form validation for all user inputs

2. **Authentication**:
   - Session verification for all statement operations
   - Timeout for sensitive operations

3. **Audit Requirements**:
   - Logging of statement access
   - Payment action audit trail
   - Error tracking for failed operations

4. **Compliance**:
   - ADA/WCAG 2.1 accessibility compliance
   - Financial data display requirements
   - Payment processing standards

## Timeline

### Phase 1: Core Architecture (Weeks 1-2)

- Week 1: Design component registry and base components
- Week 2: Implement statement list view with filtering

### Phase 2: Credit Statements (Weeks 3-4)

- Week 3: Credit statement card and detail components
- Week 4: Payment functionality and history visualization

### Phase 3: Checking and Savings Statements (Weeks 5-6)

- Week 5: Checking statement implementation
- Week 6: Savings statement implementation

### Phase 4: Polish and Documentation (Weeks 7-8)

- Week 7: Accessibility improvements and testing
- Week 8: Documentation and final testing

## Monitoring & Success Metrics

1. **User Engagement**:
   - Statement view frequency
   - Time spent on statement details
   - Action completion rate (payments, etc.)

2. **Performance Metrics**:
   - Statement list load time
   - Chart rendering performance
   - API response time

3. **Accessibility Metrics**:
   - WCAG compliance score
   - Keyboard navigation success rate
   - Screen reader compatibility score

4. **User Satisfaction**:
   - Feature-specific user feedback
   - Task completion rate
   - Support ticket reduction

## Team Impact

1. **Frontend Team**:
   - New component patterns to learn
   - Registry pattern implementation
   - Component testing requirements

2. **Backend Team**:
   - API alignment with frontend requirements
   - Type-specific data requirements

3. **QA Team**:
   - Expanded test cases for each statement type
   - Accessibility testing procedures
   - Feature flag testing scenarios

4. **Design Team**:
   - Type-specific visualization patterns
   - Mobile-responsive design requirements
   - Accessibility standards implementation

## Related Documents

- [ADR-025: Statement Types Expansion](/code/debtonator/docs/adr/backend/025-statement-types.md)
- [ADR-024: Feature Flag System](/code/debtonator/docs/adr/backend/024-feature-flags.md)
- [ADR-028: Feature Flag Management Frontend](/code/debtonator/docs/adr/frontend/028-feature-flag-management-frontend.md)
- Backend API documentation for statement endpoints
- Design system guidelines for financial data visualization

## Notes

1. **Assumptions**:
   - The backend API will provide statement type information
   - The feature flag system is operational
   - Statement types will follow the patterns defined in ADR-025
   - Mobile devices will be a significant portion of users

2. **Open Questions**:
   - Should specialized transaction views be part of statement components?
   - How detailed should historical statement visualization be?
   - What is the optimal balance between generic and specialized components?

3. **Future Considerations**:
   - Integration with loan and investment statement types
   - PDF export functionality for statements
   - Tax document integration
   - Cross-statement analytics

## Updates

| Date | Revision | Author | Description |
|------|-----------|---------|-------------|
| 2025-04-23 | 1.0 | Frontend Architect | Initial version |
