'use client';

import { Activity } from 'lucide-react';

export function Header() {
  return (
    <header className="border-b border-[#262626] bg-[#0a0a0a]">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-blue-500/10">
            <Activity className="w-6 h-6 text-blue-500" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-[#fafafa]">Sentra</h1>
            <p className="text-xs text-[#a1a1aa]">Social Media Sentiment Analysis</p>
          </div>
        </div>
      </div>
    </header>
  );
}
