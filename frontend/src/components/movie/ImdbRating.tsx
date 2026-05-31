'use client';

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
    <div className="flex items-center gap-2">
      <span className="rounded bg-[#F5C518] px-1.5 py-0.5 text-[11px] font-black text-black">
        IMDb
      </span>
      <span className="text-xs font-semibold text-white">
        {rating.toFixed(1)}/10
      </span>
      {votes && (
        <span className="text-xs text-zinc-500">{formatVotes(votes)}</span>
      )}
    </div>
  );
}
