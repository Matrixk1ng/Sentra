import { SearchResponse, HistoryResponse } from '@/types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '';

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

export async function searchSentiment(
  keyword: string,
  source: string = 'all'
): Promise<SearchResponse> {
  const params = new URLSearchParams({
    q: keyword,
    source: source,
  });

  const res = await fetch(`${API_BASE}/search?${params}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Search failed' }));
    throw new ApiError(res.status, error.detail || 'Search failed');
  }

  return res.json();
}

export async function getHistory(
  keyword: string,
  days: number = 7
): Promise<HistoryResponse> {
  const params = new URLSearchParams({
    q: keyword,
    days: days.toString(),
  });

  const res = await fetch(`${API_BASE}/history?${params}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'History fetch failed' }));
    throw new ApiError(res.status, error.detail || 'History fetch failed');
  }

  return res.json();
}

export async function checkHealth(): Promise<{
  status: string;
  database: string;
  sentimentModel: string;
  reddit: string;
  youtube: string;
}> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) {
    throw new ApiError(res.status, 'Health check failed');
  }
  return res.json();
}
