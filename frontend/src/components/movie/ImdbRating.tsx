'use client';

import { Star } from 'lucide-react';

function formatVotes(votes?: number): string {
  if (!votes) return '';
  if (votes >= 1_000_000) return `${(votes / 1_000_000).toFixed(1)}M`;
  if (votes >= 1_000) return `${Math.round(votes / 1_000)}K`;
  return String(votes);
}

interface ImdbRatingProps {
  rating: number;
  votes?: number;
}

export default function ImdbRating({ rating, votes }: ImdbRatingProps) {
  return (
    <div className="flex items-center gap-1.5">
      <Star className="h-3 w-3 fill-[#F5C518] text-[#F5C518]" />
      <span className="text-[13px] font-semibold text-white">{rating.toFixed(1)}</span>
      <span className="text-[12px] text-zinc-500">
        IMDb
        {votes && <span className="text-zinc-600"> · {formatVotes(votes)} ratings</span>}
      </span>
    </div>
  );
}
