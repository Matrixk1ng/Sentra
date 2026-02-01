'use client';

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { DailySentiment } from '@/types';

interface SentimentTrendChartProps {
  data: DailySentiment[] | null;
  isLoading: boolean;
}

const COLORS = {
  positive: '#22c55e',
  negative: '#ef4444',
  neutral: '#6b7280',
};

export function SentimentTrendChart({ data, isLoading }: SentimentTrendChartProps) {
  if (isLoading) {
    return (
      <Card className="bg-[#141414] border-[#262626]">
        <CardHeader>
          <CardTitle className="text-[#fafafa] text-lg">Sentiment Trend</CardTitle>
        </CardHeader>
        <CardContent className="h-[280px]">
          <Skeleton className="w-full h-full" />
        </CardContent>
      </Card>
    );
  }

  if (!data || data.length === 0) {
    return (
      <Card className="bg-[#141414] border-[#262626]">
        <CardHeader>
          <CardTitle className="text-[#fafafa] text-lg">Sentiment Trend</CardTitle>
        </CardHeader>
        <CardContent className="flex items-center justify-center h-[280px] text-[#a1a1aa]">
          <div className="text-center">
            <p>No historical data available</p>
            <p className="text-sm mt-1">Search more to build history</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Format date for display
  const formattedData = data.map(item => ({
    ...item,
    dateFormatted: new Date(item.date).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    }),
  }));

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-[#1a1a1a] border border-[#262626] rounded-lg px-3 py-2 shadow-lg">
          <p className="text-[#fafafa] font-medium mb-1">{label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.name}: {entry.value}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <Card className="bg-[#141414] border-[#262626]">
      <CardHeader>
        <CardTitle className="text-[#fafafa] text-lg">Sentiment Trend</CardTitle>
      </CardHeader>
      <CardContent className="h-[280px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={formattedData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#262626" />
            <XAxis
              dataKey="dateFormatted"
              stroke="#6b7280"
              tick={{ fill: '#a1a1aa', fontSize: 12 }}
              tickLine={{ stroke: '#262626' }}
            />
            <YAxis
              stroke="#6b7280"
              tick={{ fill: '#a1a1aa', fontSize: 12 }}
              tickLine={{ stroke: '#262626' }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              verticalAlign="bottom"
              height={36}
              formatter={(value: string) => (
                <span className="text-[#a1a1aa] text-sm capitalize">{value}</span>
              )}
            />
            <Line
              type="monotone"
              dataKey="positive"
              name="Positive"
              stroke={COLORS.positive}
              strokeWidth={2}
              dot={{ fill: COLORS.positive, strokeWidth: 0, r: 3 }}
              activeDot={{ r: 5 }}
            />
            <Line
              type="monotone"
              dataKey="negative"
              name="Negative"
              stroke={COLORS.negative}
              strokeWidth={2}
              dot={{ fill: COLORS.negative, strokeWidth: 0, r: 3 }}
              activeDot={{ r: 5 }}
            />
            <Line
              type="monotone"
              dataKey="neutral"
              name="Neutral"
              stroke={COLORS.neutral}
              strokeWidth={2}
              dot={{ fill: COLORS.neutral, strokeWidth: 0, r: 3 }}
              activeDot={{ r: 5 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
