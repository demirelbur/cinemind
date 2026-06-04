'use client';

import { CheckCircle2, Loader2 } from 'lucide-react';
import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

const STEPS = [
  'Understanding request',
  'Searching database',
  'Ranking recommendations',
];

export default function SearchLoading() {
  const [activeIndex, setActiveIndex] = useState(0);

  useEffect(() => {
    let cancelled = false;
    const show = setTimeout(() => { if (!cancelled) setActiveIndex(1); }, 400);
    const rank = setTimeout(() => { if (!cancelled) setActiveIndex(2); }, 900);
    return () => { cancelled = true; clearTimeout(show); clearTimeout(rank); };
  }, []);

  return (
    <motion.div
      className="rounded-2xl border border-white/[0.06] bg-zinc-900/30 p-6"
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <p className="mb-4 text-[15px] font-medium text-zinc-300">
        Searching movies...
      </p>
      <div className="space-y-3">
        {STEPS.map((step, i) => {
          const done = i < activeIndex;
          const active = i === activeIndex;
          return (
            <div key={step} className="flex items-center gap-3">
              {done ? (
                <CheckCircle2 className="h-4 w-4 text-green-400" />
              ) : active ? (
                <Loader2 className="h-4 w-4 animate-spin text-red-400" />
              ) : (
                <div className="h-4 w-4 rounded-full border border-zinc-700" />
              )}
              <span
                className={`text-[13px] ${
                  done ? 'text-zinc-400' : active ? 'text-zinc-200' : 'text-zinc-600'
                }`}
              >
                {step}
              </span>
            </div>
          );
        })}
      </div>
    </motion.div>
  );
}
