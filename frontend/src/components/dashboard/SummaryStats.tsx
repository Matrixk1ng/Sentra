'use client';

import { TrendingUp, TrendingDown, Hash, BarChart3 } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { SentimentSummary } from '@/types';
import { formatPercentage } from '@/lib/utils';

interface SummaryStatsProps {
  data: SentimentSummary | null;
  isLoading: boolean;
}

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactNode;
  iconColor: string;
  trend?: 'up' | 'down' | null;
}

function StatCard({ title, value, subtitle, icon, iconColor, trend }: StatCardProps) {
  return (
    <Card className="bg-[#141414] border-[#262626]">
      <CardContent className="p-4">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-[#6b7280] text-sm mb-1">{title}</p>
            <div className="flex items-center gap-2">
              <p className="text-2xl font-bold text-[#fafafa]">{value}</p>
              {trend && (
                <span className={trend === 'up' ? 'text-green-500' : 'text-red-500'}>
                  {trend === 'up' ? (
                    <TrendingUp className="w-4 h-4" />
                  ) : (
                    <TrendingDown className="w-4 h-4" />
                  )}
                </span>
              )}
            </div>
            {subtitle && (
              <p className="text-xs text-[#6b7280] mt-1">{subtitle}</p>
            )}
          </div>
          <div className={`p-2 rounded-lg ${iconColor}`}>
            {icon}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export function SummaryStats({ data, isLoading }: SummaryStatsProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Card key={i} className="bg-[#141414] border-[#262626]">
            <CardContent className="p-4">
              <Skeleton className="h-4 w-24 mb-2" />
              <Skeleton className="h-8 w-16" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (!data) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Posts"
          value="--"
          icon={<Hash className="w-5 h-5 text-blue-500" />}
          iconColor="bg-blue-500/10"
        />
        <StatCard
          title="Positive"
          value="--"
          icon={<TrendingUp className="w-5 h-5 text-green-500" />}
          iconColor="bg-green-500/10"
        />
        <StatCard
          title="Negative"
          value="--"
          icon={<TrendingDown className="w-5 h-5 text-red-500" />}
          iconColor="bg-red-500/10"
        />
        <StatCard
          title="Avg. Score"
          value="--"
          icon={<BarChart3 className="w-5 h-5 text-purple-500" />}
          iconColor="bg-purple-500/10"
        />
      </div>
    );
  }

  const positivePercent = formatPercentage(data.positive, data.total);
  const negativePercent = formatPercentage(data.negative, data.total);
  const dominantSentiment = data.positive > data.negative ? 'up' : data.negative > data.positive ? 'down' : null;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard
        title="Total Posts"
        value={data.total.toLocaleString()}
        subtitle="Analyzed from sources"
        icon={<Hash className="w-5 h-5 text-blue-500" />}
        iconColor="bg-blue-500/10"
      />
      <StatCard
        title="Positive"
        value={positivePercent}
        subtitle={`${data.positive} posts`}
        icon={<TrendingUp className="w-5 h-5 text-green-500" />}
        iconColor="bg-green-500/10"
        trend={dominantSentiment === 'up' ? 'up' : null}
      />
      <StatCard
        title="Negative"
        value={negativePercent}
        subtitle={`${data.negative} posts`}
        icon={<TrendingDown className="w-5 h-5 text-red-500" />}
        iconColor="bg-red-500/10"
        trend={dominantSentiment === 'down' ? 'down' : null}
      />
      <StatCard
        title="Neutral"
        value={formatPercentage(data.neutral, data.total)}
        subtitle={`${data.neutral} posts`}
        icon={<BarChart3 className="w-5 h-5 text-gray-500" />}
        iconColor="bg-gray-500/10"
      />
    </div>
  );
}
