// API Response Types

export interface Post {
  id: string;
  text: string;
  source: 'reddit' | 'youtube';
  sentiment: 'positive' | 'negative' | 'neutral';
  score: number;
  authorName?: string;
  sourceUrl?: string;
  createdAt: string;
}

export interface SentimentSummary {
  total: number;
  positive: number;
  negative: number;
  neutral: number;
}

export interface SearchResponse {
  searchId: string;
  keyword: string;
  source: string;
  posts: Post[];
  summary: SentimentSummary;
  fetchedAt: string;
  cached: boolean;
}

export interface DailySentiment {
  date: string;
  positive: number;
  negative: number;
  neutral: number;
}

export interface HistoryPeriod {
  start: string;
  end: string;
}

export interface HistoryResponse {
  keyword: string;
  period: HistoryPeriod;
  data: DailySentiment[];
}

// UI State Types

export type SourceType = 'all' | 'reddit' | 'youtube';
export type SentimentFilter = 'all' | 'positive' | 'negative' | 'neutral';
export type SortOption = 'recent' | 'score';

export interface SearchState {
  keyword: string;
  source: SourceType;
  isLoading: boolean;
  error: string | null;
  data: SearchResponse | null;
  history: HistoryResponse | null;
}
