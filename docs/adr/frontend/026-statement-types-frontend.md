# ADR-026: Statement Type Expansion - Frontend Implementation

## Status

Proposed

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

```
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

### Feature Flag Integration

The frontend implementation will respect the same feature flags as the backend:

```typescript
// src/services/feature-flags.ts
import { API } from './api';

export class FeatureFlagService {
  private flags: Record<string, boolean> = {};
  private initialized: boolean = false;
  
  constructor(private api: API) {}
  
  async initialize(): Promise<void> {
    if (this.initialized) return;
    
    try {
      const response = await this.api.get('/api/feature-flags');
      this.flags = response.data.reduce((acc: Record<string, boolean>, flag: any) => {
        acc[flag.name] = flag.enabled;
        return acc;
      }, {});
      this.initialized = true;
    } catch (error) {
      console.error('Failed to initialize feature flags:', error);
      // Default fallback flags for critical functionality
      this.flags = {
        'BANKING_ACCOUNT_TYPES_ENABLED': true
      };
    }
  }
  
  isEnabled(flagName: string): boolean {
    // Banking statement types are always enabled as core functionality
    if (flagName === 'BANKING_ACCOUNT_TYPES_ENABLED') {
      return true;
    }
    
    return this.flags[flagName] || false;
  }
}
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

## Expected Benefits

1. **Improved User Experience**: Type-specific components provide relevant information and actions
2. **Enhanced Data Visualization**: Specialized charts and metrics for each statement type
3. **Consistent Design Language**: Unified component structure with type-specific variations
4. **Future Extensibility**: Easy addition of new statement types through the registry pattern
5. **Better Accessibility**: Properly structured components with screen reader support
6. **Feature Control**: Seamless integration with backend feature flags

## Alternatives Considered

1. **Generic Component with Conditional Rendering**
   - Pros: Simpler implementation, less code duplication
   - Cons: Complex conditional logic, harder to maintain and extend

2. **Separated Route Structure for Each Type**
   - Pros: Clear separation of concerns, easier code splitting
   - Cons: Inconsistent user experience, duplication of common functionality

3. **Custom Rendering Logic in Parent Components**
   - Pros: More control over rendering, less abstraction layers
   - Cons: Logic scattered across application, harder to maintain consistent behavior

## References

- [ADR-025: Statement Type Expansion](../adr/backend/025-statement-types.md)
- [React Component Composition Patterns](https://reactjs.org/docs/composition-vs-inheritance.html)
- [WAI-ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/)
- [Recharts Documentation](https://recharts.org/en-US/)
