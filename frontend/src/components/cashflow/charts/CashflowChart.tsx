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
  Brush
} from 'recharts';
import { CashflowForecast } from '../../../types/cashflow';
import { formatCurrency } from '../../../utils/formatters';

interface CashflowChartProps {
  data: CashflowForecast[];
  onDateRangeChange?: (start: Date, end: Date) => void;
  onPointClick?: (date: Date) => void;
}

const CashflowChart: React.FC<CashflowChartProps> = ({
  data,
  onDateRangeChange,
  onPointClick
}) => {
  const formattedData = useMemo(() => {
    return data.map(item => ({
      ...item,
      date: new Date(item.date).toLocaleDateString(),
    }));
  }, [data]);

  const handleBrushChange = (range: { startIndex?: number; endIndex?: number }) => {
    if (range && range.startIndex !== undefined && range.endIndex !== undefined && onDateRangeChange) {
      const startDate = new Date(data[range.startIndex].date);
      const endDate = new Date(data[range.endIndex].date);
      onDateRangeChange(startDate, endDate);
    }
  };

  const handleClick = (point: { activePayload?: Array<{ payload: CashflowForecast & { date: string } }> }) => {
    if (point && point.activePayload && onPointClick) {
      const date = new Date(point.activePayload[0].payload.date);
      onPointClick(date);
    }
  };

  return (
    <div style={{ width: '100%', height: 400 }}>
      <ResponsiveContainer>
        <LineChart
          data={formattedData}
          margin={{ top: 20, right: 30, left: 20, bottom: 10 }}
          onClick={handleClick}
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
          <Legend />
          <Line
            type="monotone"
            dataKey="balance"
            stroke="#8884d8"
            name="Balance"
            dot={false}
            activeDot={{ r: 8 }}
          />
          <Line
            type="monotone"
            dataKey="forecast"
            stroke="#82ca9d"
            name="Forecast"
            dot={false}
            activeDot={{ r: 8 }}
          />
          <Brush
            dataKey="date"
            height={30}
            stroke="#8884d8"
            onChange={handleBrushChange}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default CashflowChart;
