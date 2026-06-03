'use client';

import { Check } from 'lucide-react';

interface WhyItMatchesProps {
  reason: string;
  tags?: string[];
}

const MAX_REASON_CHARS = 160;

export default function WhyItMatches({ reason, tags }: WhyItMatchesProps) {
  const displayTags = tags?.filter(Boolean).slice(0, 4) || [];

  const reasonLong = reason.length > MAX_REASON_CHARS;
  const displayReason = reasonLong ? reason.slice(0, reason.lastIndexOf(' ', MAX_REASON_CHARS)) + '…' : reason;

  return (
    <div className="rounded-xl border border-zinc-700/50 bg-zinc-900/60 p-3">
      {displayTags.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {displayTags.map((tag) => (
            <span
              key={tag}
              className="inline-flex h-5 items-center gap-1 rounded-full border border-[rgba(34,197,94,0.25)] bg-[rgba(34,197,94,0.1)] px-2 text-[11px] font-medium text-green-400"
            >
              <Check className="h-2 w-2" />
              {tag}
            </span>
          ))}
        </div>
      )}
      <p className="mt-1.5 text-[12px] leading-snug text-zinc-300">
        {displayReason}
      </p>
    </div>
  );
}
