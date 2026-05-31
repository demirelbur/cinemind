'use client';

import { motion } from 'framer-motion';

interface MatchScoreRingProps {
  score: number;
}

function getStrokeColors(score: number): { c1: string; c2: string } {
  if (score >= 95) return { c1: '#FF1F2D', c2: '#ff5f6d' };
  if (score >= 80) return { c1: '#FF6B35', c2: '#FF1F2D' };
  if (score >= 65) return { c1: '#FBBF24', c2: '#F59E0B' };
  return { c1: '#71717A', c2: '#52525B' };
}

export default function MatchScoreRing({ score }: MatchScoreRingProps) {
  const clamped = Math.max(0, Math.min(100, Math.round(score)));
  const { c1, c2 } = getStrokeColors(clamped);

  return (
    <motion.div
      className="relative hidden h-20 w-20 flex-shrink-0 md:flex"
      initial={{ opacity: 0, scale: 0.85 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ type: 'spring', stiffness: 200, damping: 18 }}
    >
      <svg viewBox="0 0 100 100" className="h-full w-full">
        <defs>
          <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor={c1} />
            <stop offset="100%" stopColor={c2} />
          </linearGradient>
        </defs>
        <circle
          cx="50"
          cy="50"
          r="42"
          stroke="rgba(255,255,255,0.08)"
          strokeWidth="8"
          fill="none"
        />
        <motion.circle
          cx="50"
          cy="50"
          r="42"
          stroke="url(#scoreGradient)"
          strokeWidth="8"
          fill="none"
          strokeLinecap="round"
          strokeDasharray={`${clamped * 2.64} 264`}
          initial={{ pathLength: 0 }}
          animate={{ pathLength: clamped / 100 }}
          transition={{ duration: 1, ease: 'easeOut' }}
          style={{ transformOrigin: 'center', transform: 'rotate(-90deg)' }}
        />
      </svg>

      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span
          className={`font-bold leading-none tracking-tight text-white ${
            clamped >= 100 ? 'text-[24px]' : 'text-[28px]'
          }`}
        >
          {clamped}
          <span className="align-super text-[13px]">%</span>
        </span>
        <span className="mt-1 text-[11px] leading-none text-zinc-400">match</span>
      </div>
    </motion.div>
  );
}
