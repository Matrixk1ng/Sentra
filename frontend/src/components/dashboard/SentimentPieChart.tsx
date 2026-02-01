'use client';

import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { SentimentSummary } from '@/types';

interface SentimentPieChartProps {
  data: SentimentSummary | null;
  isLoading: boolean;
}

const COLORS = {
  positive: '#22c55e',
  negative: '#ef4444',
  neutral: '#6b7280',
};

export function SentimentPieChart({ data, isLoading }: SentimentPieChartProps) {
  if (isLoading) {
    return (
      <Card className="bg-[#141414] border-[#262626]">
        <CardHeader>
          <CardTitle className="text-[#fafafa] text-lg">Sentiment Distribution</CardTitle>
        </CardHeader>
        <CardContent className="flex items-center justify-center h-[280px]">
          <Skeleton className="w-48 h-48 rounded-full" />
        </CardContent>
      </Card>
    );
  }

  if (!data || data.total === 0) {
    return (
      <Card className="bg-[#141414] border-[#262626]">
        <CardHeader>
          <CardTitle className="text-[#fafafa] text-lg">Sentiment Distribution</CardTitle>
        </CardHeader>
        <CardContent className="flex items-center justify-center h-[280px] text-[#a1a1aa]">
          No data available
        </CardContent>
      </Card>
    );
  }

  const chartData = [
    { name: 'Positive', value: data.positive, color: COLORS.positive },
    { name: 'Negative', value: data.negative, color: COLORS.negative },
    { name: 'Neutral', value: data.neutral, color: COLORS.neutral },
  ].filter(item => item.value > 0);

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const item = payload[0];
      const percentage = ((item.value / data.total) * 100).toFixed(1);
      return (
        <div className="bg-[#1a1a1a] border border-[#262626] rounded-lg px-3 py-2 shadow-lg">
          <p className="text-[#fafafa] font-medium">{item.name}</p>
          <p className="text-[#a1a1aa] text-sm">
            {item.value} posts ({percentage}%)
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <Card className="bg-[#141414] border-[#262626]">
      <CardHeader>
        <CardTitle className="text-[#fafafa] text-lg">Sentiment Distribution</CardTitle>
      </CardHeader>
      <CardContent className="h-[280px]">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="45%"
              innerRadius={60}
              outerRadius={90}
              paddingAngle={2}
              dataKey="value"
              animationBegin={0}
              animationDuration={500}
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
            <Legend
              verticalAlign="bottom"
              height={36}
              formatter={(value: string) => (
                <span className="text-[#a1a1aa] text-sm">{value}</span>
              )}
            />
            {/* Center text */}
            <text
              x="50%"
              y="42%"
              textAnchor="middle"
              dominantBaseline="middle"
              className="fill-[#fafafa] text-2xl font-bold"
            >
              {data.total}
            </text>
            <text
              x="50%"
              y="52%"
              textAnchor="middle"
              dominantBaseline="middle"
              className="fill-[#a1a1aa] text-xs"
            >
              posts
            </text>
          </PieChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
