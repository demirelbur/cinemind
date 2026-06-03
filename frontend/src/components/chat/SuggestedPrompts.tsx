'use client';

import { Sparkles } from 'lucide-react';
import { motion } from 'framer-motion';

const PROMPTS = [
  'Recommend 3 dark sci-fi movies from the 80s',
  'Movies like Interstellar but more emotional',
  'Give me 3 comedy movies from the 2000s',
  'Family-friendly adventure movies',
  'Top-rated thrillers, no horror please',
  'Underrated horror films for adults',
];

interface SuggestedPromptsProps {
  onSelect: (prompt: string) => void;
}

export default function SuggestedPrompts({ onSelect }: SuggestedPromptsProps) {
  return (
    <div className="mx-auto text-center">
      <div className="mx-auto max-w-[520px]">
        {/* Headline */}
        <motion.div
          className="mb-3 flex items-center justify-center gap-2"
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Sparkles className="h-5 w-5 text-red-400" />
          <h2 className="text-[26px] font-bold tracking-tight text-white md:text-[30px]">
            Ask for movies{' '}
            <span className="bg-gradient-to-r from-white to-zinc-400 bg-clip-text text-transparent">
              the way you think
            </span>
          </h2>
        </motion.div>

        {/* Subtitle */}
        <motion.p
          className="mb-4 text-[15px] leading-relaxed text-zinc-400"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.15 }}
        >
          Be as specific or broad as you like—genre, mood, decade, actor, or vibe.
        </motion.p>

        {/* Trust line */}
        <motion.p
          className="mb-6 text-[13px] leading-relaxed text-zinc-500"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          Recommendations are ranked by relevance, IMDb rating, and movie metadata.
        </motion.p>
      </div>

      {/* Chips label */}
      <motion.p
        className="mb-5 text-[12px] font-semibold uppercase tracking-wider text-zinc-600"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.25 }}
      >
        Try one of these
      </motion.p>

      {/* Clickable prompt chips */}
      <motion.div
        className="mx-auto flex max-w-[860px] flex-wrap justify-center gap-4"
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        {PROMPTS.map((prompt, i) => (
          <motion.button
            key={prompt}
            onClick={() => onSelect(prompt)}
            className="min-w-[220px] max-w-[400px] rounded-full border border-white/[0.08] bg-white/[0.04] px-5 py-2.5 text-[13px] font-medium text-zinc-300 transition-all hover:border-white/[0.14] hover:bg-white/[0.07] hover:text-white md:min-w-[260px] md:max-w-[420px]"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.35 + i * 0.04 }}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            {prompt}
          </motion.button>
        ))}
      </motion.div>
    </div>
  );
}
