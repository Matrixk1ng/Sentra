'use client';

import { useState, useMemo } from 'react';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { PostCard } from './PostCard';
import { Post, SentimentFilter, SortOption } from '@/types';

interface PostsListProps {
  posts: Post[];
  isLoading: boolean;
}

const POSTS_PER_PAGE = 20;

export function PostsList({ posts, isLoading }: PostsListProps) {
  const [filter, setFilter] = useState<SentimentFilter>('all');
  const [sortBy, setSortBy] = useState<SortOption>('score');
  const [visibleCount, setVisibleCount] = useState(POSTS_PER_PAGE);

  const filteredAndSortedPosts = useMemo(() => {
    let result = [...posts];

    // Filter
    if (filter !== 'all') {
      result = result.filter(post => post.sentiment === filter);
    }

    // Sort
    if (sortBy === 'score') {
      result.sort((a, b) => b.score - a.score);
    } else {
      result.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
    }

    return result;
  }, [posts, filter, sortBy]);

  const visiblePosts = filteredAndSortedPosts.slice(0, visibleCount);
  const hasMore = visibleCount < filteredAndSortedPosts.length;

  const handleLoadMore = () => {
    setVisibleCount(prev => prev + POSTS_PER_PAGE);
  };

  // Reset visible count when filter changes
  const handleFilterChange = (value: string) => {
    setFilter(value as SentimentFilter);
    setVisibleCount(POSTS_PER_PAGE);
  };

  if (isLoading) {
    return (
      <Card className="bg-[#141414] border-[#262626]">
        <CardHeader>
          <CardTitle className="text-[#fafafa] text-lg">Recent Posts</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="p-4 rounded-lg border border-[#262626]">
              <div className="flex gap-2 mb-2">
                <Skeleton className="h-5 w-16" />
                <Skeleton className="h-5 w-20" />
              </div>
              <Skeleton className="h-4 w-full mb-2" />
              <Skeleton className="h-4 w-3/4" />
            </div>
          ))}
        </CardContent>
      </Card>
    );
  }

  if (posts.length === 0) {
    return (
      <Card className="bg-[#141414] border-[#262626]">
        <CardHeader>
          <CardTitle className="text-[#fafafa] text-lg">Recent Posts</CardTitle>
        </CardHeader>
        <CardContent className="flex items-center justify-center h-[200px] text-[#a1a1aa]">
          No posts to display
        </CardContent>
      </Card>
    );
  }

  const filterCounts = {
    all: posts.length,
    positive: posts.filter(p => p.sentiment === 'positive').length,
    negative: posts.filter(p => p.sentiment === 'negative').length,
    neutral: posts.filter(p => p.sentiment === 'neutral').length,
  };

  return (
    <Card className="bg-[#141414] border-[#262626]">
      <CardHeader>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <CardTitle className="text-[#fafafa] text-lg">Recent Posts</CardTitle>
          
          <div className="flex items-center gap-3">
            <Tabs value={filter} onValueChange={handleFilterChange}>
              <TabsList className="bg-[#0a0a0a] border border-[#262626]">
                <TabsTrigger value="all" className="data-[state=active]:bg-[#262626] text-[#a1a1aa] data-[state=active]:text-[#fafafa]">
                  All ({filterCounts.all})
                </TabsTrigger>
                <TabsTrigger value="positive" className="data-[state=active]:bg-green-500/20 data-[state=active]:text-green-500 text-[#a1a1aa]">
                  Positive ({filterCounts.positive})
                </TabsTrigger>
                <TabsTrigger value="negative" className="data-[state=active]:bg-red-500/20 data-[state=active]:text-red-500 text-[#a1a1aa]">
                  Negative ({filterCounts.negative})
                </TabsTrigger>
                <TabsTrigger value="neutral" className="data-[state=active]:bg-gray-500/20 data-[state=active]:text-gray-400 text-[#a1a1aa]">
                  Neutral ({filterCounts.neutral})
                </TabsTrigger>
              </TabsList>
            </Tabs>

            <Select value={sortBy} onValueChange={(value) => setSortBy(value as SortOption)}>
              <SelectTrigger className="w-[140px] bg-[#0a0a0a] border-[#262626] text-[#fafafa]">
                <SelectValue placeholder="Sort by" />
              </SelectTrigger>
              <SelectContent className="bg-[#141414] border-[#262626]">
                <SelectItem value="score" className="text-[#fafafa] focus:bg-[#262626]">Highest Score</SelectItem>
                <SelectItem value="recent" className="text-[#fafafa] focus:bg-[#262626]">Most Recent</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3 max-h-[600px] overflow-y-auto pr-2">
          {visiblePosts.map(post => (
            <PostCard key={post.id} post={post} />
          ))}
        </div>
        
        {hasMore && (
          <div className="mt-4 text-center">
            <Button
              variant="outline"
              onClick={handleLoadMore}
              className="bg-transparent border-[#262626] text-[#a1a1aa] hover:bg-[#262626] hover:text-[#fafafa]"
            >
              Load More ({filteredAndSortedPosts.length - visibleCount} remaining)
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
