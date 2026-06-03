'use client';

import { motion } from 'framer-motion';

interface MatchScoreBadgeProps {
  score: number;
}

function getScoreColor(score: number): string {
  if (score >= 95) return '#FF1F2D';
  if (score >= 85) return '#FF6B35';
  if (score >= 70) return '#FBBF24';
  return '#71717A';
}

function getScoreLabel(score: number): string {
  if (score >= 95) return 'Perfect Match';
  if (score >= 85) return 'Strong Match';
  if (score >= 75) return 'Good Match';
  if (score >= 65) return 'Worth Considering';
  return 'Alternative Pick';
}

export default function MatchScoreBadge({ score }: MatchScoreBadgeProps) {
  const clamped = Math.max(0, Math.min(100, Math.round(score)));
  const color = getScoreColor(clamped);
  const label = getScoreLabel(clamped);

  return (
    <motion.div
      className="flex flex-shrink-0 flex-col items-end"
      initial={{ opacity: 0, x: 12 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.4, delay: 0.2 }}
    >
      <div className="flex items-baseline gap-0.5">
        <span
          className="text-[24px] font-bold leading-none tracking-tight"
          style={{ color }}
        >
          {clamped}
        </span>
        <span className="text-[13px] font-semibold text-zinc-500">%</span>
      </div>
      <span className="mt-0.5 text-[10px] font-medium text-zinc-500">
        {label}
      </span>
    </motion.div>
  );
}
