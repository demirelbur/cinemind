'use client';

import { Check } from 'lucide-react';
import { motion } from 'framer-motion';

import InfoChip from '@/components/movie/InfoChip';

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

function highlightTerms(text: string, terms: string[]): React.ReactNode[] {
  if (!terms.length) return [text];
  const escaped = terms.map((t) => t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
  const regex = new RegExp(`(${escaped.join('|')})`, 'gi');
  const parts = text.split(regex);
  return parts.map((part, i) =>
    regex.test(part) ? (
      <span key={i} className="text-white font-medium">
        {part}
      </span>
    ) : (
      <span key={i}>{part}</span>
    ),
  );
}

export default function WhyItMatches({
  reason,
  details,
  genre,
  decade,
  audience,
}: WhyItMatchesProps) {
  const highlights = [genre, decade, audience].filter(Boolean) as string[];
  const { genreMatch, decadeMatch, audienceFit, similarity } = details;

  const chips = [
    { label: genre || 'Genre', active: genreMatch },
    { label: decade || 'Decade', active: decadeMatch },
    { label: audience || 'Audience', active: audienceFit },
    { label: 'High similarity', active: similarity },
  ].filter((c) => c.active);

  return (
    <motion.div
      className="rounded-2xl border border-white/[0.06] bg-white/[0.02] p-5"
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2, duration: 0.4 }}
    >
      <h4 className="mb-3 text-sm font-semibold text-zinc-400">
        Why this recommendation
      </h4>
      <p className="mb-4 text-[15px] leading-relaxed text-zinc-300">
        {highlightTerms(reason, highlights)}
      </p>
      <div className="flex flex-wrap gap-2">
        {chips.map((chip) => (
          <div
            key={chip.label}
            className="inline-flex h-7 items-center gap-1.5 rounded-full border border-[rgba(34,197,94,0.2)] bg-[rgba(34,197,94,0.08)] px-3 text-xs font-medium text-green-400"
          >
            <Check className="h-3 w-3" />
            <span>{chip.label}</span>
          </div>
        ))}
      </div>
    </motion.div>
  );
}
