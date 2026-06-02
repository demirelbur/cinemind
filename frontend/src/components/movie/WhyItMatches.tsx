'use client';

import { Check } from 'lucide-react';

interface WhyItMatchesProps {
  reason: string;
  details: {
    genreMatch: boolean;
    decadeMatch: boolean;
    audienceFit: boolean;
    similarity: boolean;
  };
  genre?: string;
  decade?: string;
  audience?: string;
}

export default function WhyItMatches({
  reason,
  details,
  genre,
  decade,
  audience,
}: WhyItMatchesProps) {
  const { genreMatch, decadeMatch, audienceFit, similarity } = details;

  const chips = [
    { label: genre || 'Genre', active: genreMatch },
    { label: decade || 'Decade', active: decadeMatch },
    { label: audience || 'Audience', active: audienceFit },
    { label: 'High similarity', active: similarity },
  ].filter((c) => c.active);

  return (
    <div className="space-y-1.5">
      {/* Chips first — most scannable info */}
      {chips.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {chips.map((chip) => (
            <span
              key={chip.label}
              className="inline-flex h-6 items-center gap-1 rounded-full border border-[rgba(34,197,94,0.2)] bg-[rgba(34,197,94,0.08)] px-2.5 text-[11px] font-medium text-green-400"
            >
              <Check className="h-2.5 w-2.5" />
              {chip.label}
            </span>
          ))}
        </div>
      )}
      {/* One-line reason */}
      <p className="text-[13px] leading-snug text-zinc-400">{reason}</p>
    </div>
  );
}
