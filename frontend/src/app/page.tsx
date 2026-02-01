'use client';

import { useState, useCallback } from 'react';
import { Header, Container } from '@/components/layout';
import {
  SearchBar,
  SentimentPieChart,
  SentimentTrendChart,
  PostsList,
  SummaryStats,
  EmptyState,
  ErrorBanner,
} from '@/components/dashboard';
import { searchSentiment, getHistory } from '@/lib/api';
import { SearchResponse, HistoryResponse, SourceType } from '@/types';

export default function Dashboard() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchData, setSearchData] = useState<SearchResponse | null>(null);
  const [historyData, setHistoryData] = useState<HistoryResponse | null>(null);
  const [lastSearchParams, setLastSearchParams] = useState<{ keyword: string; source: SourceType } | null>(null);

  const handleSearch = useCallback(async (keyword: string, source: SourceType) => {
    setIsLoading(true);
    setError(null);
    setLastSearchParams({ keyword, source });

    try {
      // Fetch search results and history in parallel
      const [searchResult, historyResult] = await Promise.all([
        searchSentiment(keyword, source),
        getHistory(keyword, 7).catch(() => null), // Don't fail if history is empty
      ]);

      setSearchData(searchResult);
      setHistoryData(historyResult);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'An unexpected error occurred';
      setError(message);
      setSearchData(null);
      setHistoryData(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleRetry = useCallback(() => {
    if (lastSearchParams) {
      handleSearch(lastSearchParams.keyword, lastSearchParams.source);
    }
  }, [lastSearchParams, handleSearch]);

  const hasData = searchData !== null;

  return (
    <div className="min-h-screen bg-[#0a0a0a]">
      <Header />
      
      <Container>
        {/* Search Bar */}
        <div className="mb-8">
          <SearchBar onSearch={handleSearch} isLoading={isLoading} />
        </div>

        {/* Error Banner */}
        {error && (
          <div className="mb-6">
            <ErrorBanner message={error} onRetry={handleRetry} />
          </div>
        )}

        {/* Empty State */}
        {!hasData && !isLoading && !error && (
          <EmptyState />
        )}

        {/* Dashboard Content */}
        {(hasData || isLoading) && (
          <div className="space-y-6">
            {/* Search Result Info */}
            {searchData && !isLoading && (
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-semibold text-[#fafafa]">
                    Results for &ldquo;{searchData.keyword}&rdquo;
                  </h2>
                  <p className="text-sm text-[#6b7280]">
                    {searchData.summary.total} posts analyzed from {searchData.source === 'all' ? 'all sources' : searchData.source}
                    {searchData.cached && <span className="ml-2 text-blue-500">(cached)</span>}
                  </p>
                </div>
              </div>
            )}

            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <SentimentPieChart 
                data={searchData?.summary || null} 
                isLoading={isLoading} 
              />
              <SentimentTrendChart 
                data={historyData?.data || null} 
                isLoading={isLoading} 
              />
            </div>

            {/* Summary Stats */}
            <SummaryStats 
              data={searchData?.summary || null} 
              isLoading={isLoading} 
            />

            {/* Posts List */}
            <PostsList 
              posts={searchData?.posts || []} 
              isLoading={isLoading} 
            />
          </div>
        )}
      </Container>

      {/* Footer */}
      <footer className="border-t border-[#262626] mt-12 py-6">
        <Container>
          <div className="flex items-center justify-between text-sm text-[#6b7280]">
            <p>Sentra - Social Media Sentiment Analysis</p>
            <p>Powered by HuggingFace Transformers</p>
          </div>
        </Container>
      </footer>
    </div>
  );
}
