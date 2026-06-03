'use client';

import { useState } from 'react';

interface WhyItMatchesProps {
  reason: string;
}

const MAX_REASON_CHARS = 160;

function truncateAtSentence(text: string, maxChars: number): string {
  if (text.length <= maxChars) return text;
  const window = text.slice(0, maxChars);
  const lastPeriod = window.lastIndexOf('.');
  if (lastPeriod > maxChars * 0.5) {
    return window.slice(0, lastPeriod + 1);
  }
  const lastSpace = window.lastIndexOf(' ');
  return (lastSpace > maxChars * 0.5 ? window.slice(0, lastSpace) : window.slice(0, maxChars)).replace(/\s+$/, '') + '…';
}

export default function WhyItMatches({ reason }: WhyItMatchesProps) {
  const [expanded, setExpanded] = useState(false);
  const reasonLong = reason.length > MAX_REASON_CHARS;
  const displayReason = expanded || !reasonLong ? reason : truncateAtSentence(reason, MAX_REASON_CHARS);

  return (
    <div className="rounded-xl bg-zinc-900/40 p-3">
      <p className="text-[12px] leading-snug text-zinc-300">
        {displayReason}
      </p>
      {reasonLong && !expanded && (
        <button
          onClick={() => setExpanded(true)}
          className="mt-1 text-[11px] text-zinc-500 underline underline-offset-2 hover:text-zinc-300"
        >
          Read more
        </button>
      )}
    </div>
  );
}
