'use client';

import { Search, BarChart3 } from 'lucide-react';

interface EmptyStateProps {
  title?: string;
  description?: string;
}

export function EmptyState({ 
  title = "Search for a keyword to analyze sentiment",
  description = "Enter a topic, hashtag, or keyword to see what people are saying about it on Reddit and YouTube."
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-20 px-4 text-center">
      <div className="flex items-center justify-center w-16 h-16 rounded-full bg-blue-500/10 mb-6">
        <BarChart3 className="w-8 h-8 text-blue-500" />
      </div>
      <h2 className="text-xl font-semibold text-[#fafafa] mb-2">
        {title}
      </h2>
      <p className="text-[#a1a1aa] max-w-md">
        {description}
      </p>
      <div className="mt-8 flex items-center gap-2 text-[#6b7280] text-sm">
        <Search className="w-4 h-4" />
        <span>Try searching for "AI", "climate change", or a brand name</span>
      </div>
    </div>
  );
}
