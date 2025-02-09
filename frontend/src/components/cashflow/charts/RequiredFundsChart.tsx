import React, { useMemo } from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ReferenceLine,
} from 'recharts';
import { formatCurrency } from '../../../utils/formatters';

interface RequiredFunds {
  period: string;
  required: number;
  available: number;
}

interface RequiredFundsChartProps {
  data: RequiredFunds[];
  onPeriodSelect?: (period: string) => void;
}

const RequiredFundsChart: React.FC<RequiredFundsChartProps> = ({
  data,
  onPeriodSelect
}) => {
  const formattedData = useMemo(() => {
    return data.map(item => ({
      ...item,
      deficit: Math.min(0, item.available - item.required), // Negative values for deficit
      surplus: Math.max(0, item.available - item.required), // Positive values for surplus
    }));
  }, [data]);

  const handleClick = (entry: RequiredFunds) => {
    if (onPeriodSelect) {
      onPeriodSelect(entry.period);
    }
  };

  return (
    <div style={{ width: '100%', height: 400 }}>
      <ResponsiveContainer>
        <BarChart
          data={formattedData}
          margin={{ top: 20, right: 30, left: 20, bottom: 10 }}
          onClick={(data) => data && handleClick(data.activePayload?.[0]?.payload)}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="period"
            padding={{ left: 30, right: 30 }}
          />
          <YAxis
            tickFormatter={formatCurrency}
            width={80}
          />
          <Tooltip
            formatter={(value: number) => formatCurrency(value)}
            labelFormatter={(label) => `Period: ${label}`}
          />
          <Legend />
          <ReferenceLine y={0} stroke="#000" />
          <Bar
            dataKey="required"
            fill="#8884d8"
            name="Required Funds"
          />
          <Bar
            dataKey="available"
            fill="#82ca9d"
            name="Available Funds"
          />
          <Bar
            dataKey="deficit"
            fill="#ff0000"
            name="Deficit"
            stackId="balance"
          />
          <Bar
            dataKey="surplus"
            fill="#00ff00"
            name="Surplus"
            stackId="balance"
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default RequiredFundsChart;
