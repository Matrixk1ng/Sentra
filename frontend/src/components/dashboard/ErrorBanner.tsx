'use client';

import { AlertCircle, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface ErrorBannerProps {
  message: string;
  onRetry?: () => void;
}

export function ErrorBanner({ message, onRetry }: ErrorBannerProps) {
  return (
    <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
        <p className="text-red-400 text-sm">{message}</p>
      </div>
      {onRetry && (
        <Button
          variant="outline"
          size="sm"
          onClick={onRetry}
          className="bg-transparent border-red-500/30 text-red-400 hover:bg-red-500/10 hover:text-red-300"
        >
          <RefreshCw className="w-4 h-4 mr-2" />
          Retry
        </Button>
      )}
    </div>
  );
}
