import React, { useMemo } from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';
import { Account } from '../../../types/accounts';
import { formatCurrency } from '../../../utils/formatters';

export interface AccountBalance {
  date: string;
  [accountName: string]: number | string; // Dynamic account balances
}

interface AccountBalanceChartProps {
  data: AccountBalance[];
  accounts: Account[];
  onAccountToggle?: (accountId: number) => void;
}

// Generate unique colors for each account line
const getLineColor = (index: number): string => {
  const colors = [
    '#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#0088fe',
    '#00c49f', '#ffbb28', '#ff8042', '#a4de6c', '#d0ed57'
  ];
  return colors[index % colors.length];
};

const AccountBalanceChart: React.FC<AccountBalanceChartProps> = ({
  data,
  accounts,
  onAccountToggle
}) => {
  const formattedData = useMemo(() => {
    return data.map(item => ({
      ...item,
      date: new Date(item.date).toLocaleDateString(),
    }));
  }, [data]);

  const handleLegendClick = (entry: { value: string }) => {
    const account = accounts.find(acc => acc.name === entry.value);
    if (account && onAccountToggle) {
      onAccountToggle(account.id);
    }
  };

  return (
    <div style={{ width: '100%', height: 400 }}>
      <ResponsiveContainer>
        <LineChart
          data={formattedData}
          margin={{ top: 20, right: 30, left: 20, bottom: 10 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="date"
            padding={{ left: 30, right: 30 }}
          />
          <YAxis
            tickFormatter={formatCurrency}
            width={80}
          />
          <Tooltip
            formatter={(value: number) => formatCurrency(value)}
            labelFormatter={(label) => `Date: ${label}`}
          />
          <Legend onClick={handleLegendClick} />
          {accounts.map((account, index) => (
            <Line
              key={account.id}
              type="monotone"
              dataKey={account.name}
              name={account.name}
              stroke={getLineColor(index)}
              dot={false}
              activeDot={{ r: 8 }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default AccountBalanceChart;
