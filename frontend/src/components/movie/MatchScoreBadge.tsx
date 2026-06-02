'use client';

import { motion } from 'framer-motion';

interface MatchScoreBadgeProps {
  score: number;
}

function getScoreColor(score: number): string {
  if (score >= 90) return '#FF1F2D';
  if (score >= 80) return '#FF6B35';
  if (score >= 70) return '#FBBF24';
  return '#71717A';
}

function getScoreLabel(score: number): string {
  if (score >= 90) return 'Strong Match';
  if (score >= 80) return 'Good Match';
  if (score >= 70) return 'Alternative Pick';
  return 'Consider';
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
      <div className="flex items-baseline gap-1">
        <span className="text-[28px] font-bold leading-none tracking-tight" style={{ color }}>
          {clamped}
        </span>
        <span className="text-[14px] font-semibold text-zinc-500">%</span>
      </div>
      <span className="mt-0.5 text-[11px] font-medium text-zinc-500">{label}</span>
    </motion.div>
  );
}
