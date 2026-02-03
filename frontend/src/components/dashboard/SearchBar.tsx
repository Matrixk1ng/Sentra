'use client';

import { useState } from 'react';
import { Search, Loader2 } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { SourceType } from '@/types';

interface SearchBarProps {
  onSearch: (keyword: string, source: SourceType) => void;
  isLoading: boolean;
}

export function SearchBar({ onSearch, isLoading }: SearchBarProps) {
  const [keyword, setKeyword] = useState('');
  const [source, setSource] = useState<SourceType>('all');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (keyword.trim() && !isLoading) {
      onSearch(keyword.trim(), source);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-3 w-full">
      <div className="relative flex-1">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[#a1a1aa]" />
        <Input
          type="text"
          placeholder="Search keyword or #hashtag..."
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          onKeyDown={handleKeyDown}
          className="pl-10 bg-[#141414] border-[#262626] text-[#fafafa] placeholder:text-[#6b7280] focus:border-blue-500 focus:ring-blue-500/20"
          disabled={isLoading}
        />
      </div>
      
      <Select value={source} onValueChange={(value) => setSource(value as SourceType)}>
        <SelectTrigger className="w-[140px] bg-[#141414] border-[#262626] text-[#fafafa]">
          <SelectValue placeholder="Source" />
        </SelectTrigger>
        <SelectContent className="bg-[#141414] border-[#262626]">
          <SelectItem value="all" className="text-[#fafafa] focus:bg-[#262626]">All Sources</SelectItem>
          <SelectItem value="reddit" className="text-[#fafafa] focus:bg-[#262626]">Reddit</SelectItem>
          <SelectItem value="youtube" className="text-[#fafafa] focus:bg-[#262626]">YouTube</SelectItem>
          <SelectItem value="bluesky" className="text-[#fafafa] focus:bg-[#262626]">Bluesky</SelectItem>
        </SelectContent>
      </Select>

      <Button 
        type="submit" 
        disabled={!keyword.trim() || isLoading}
        className="bg-blue-500 hover:bg-blue-600 text-white px-6"
      >
        {isLoading ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Searching
          </>
        ) : (
          'Search'
        )}
      </Button>
    </form>
  );
}
