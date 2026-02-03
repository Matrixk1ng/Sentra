'use client';

import { useState } from 'react';
import { ExternalLink } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Post } from '@/types';
import { formatRelativeTime, truncateText } from '@/lib/utils';

interface PostCardProps {
  post: Post;
}

export function PostCard({ post }: PostCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const shouldTruncate = post.text.length > 280;
  const displayText = isExpanded ? post.text : truncateText(post.text, 280);

  const sentimentVariant = post.sentiment as 'positive' | 'negative' | 'neutral';
  const sourceVariant = post.source as 'reddit' | 'youtube' | 'bluesky';

  return (
    <Card className="bg-[#141414] border-[#262626] hover:border-[#363636] transition-colors">
      <CardContent className="p-4">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            {/* Badges row */}
            <div className="flex items-center gap-2 mb-2">
              <Badge variant={sourceVariant} className="capitalize">
                {post.source}
              </Badge>
              <Badge variant={sentimentVariant} className="capitalize">
                {post.sentiment}
              </Badge>
              <span className="text-xs text-[#6b7280]">
                {Math.round(post.score * 100)}% confidence
              </span>
            </div>

            {/* Text content */}
            <p className="text-[#fafafa] text-sm leading-relaxed whitespace-pre-wrap">
              {displayText}
            </p>
            
            {shouldTruncate && (
              <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="text-blue-500 text-sm mt-1 hover:underline"
              >
                {isExpanded ? 'Show less' : 'Show more'}
              </button>
            )}

            {/* Meta info */}
            <div className="flex items-center gap-3 mt-3 text-xs text-[#6b7280]">
              {post.authorName && (
                <span className="truncate max-w-[150px]">{post.authorName}</span>
              )}
              <span>{formatRelativeTime(post.createdAt)}</span>
              {post.sourceUrl && (
                <a
                  href={post.sourceUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1 text-blue-500 hover:underline ml-auto"
                >
                  View original
                  <ExternalLink className="w-3 h-3" />
                </a>
              )}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
