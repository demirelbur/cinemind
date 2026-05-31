'use client';

import { Sparkles } from 'lucide-react';
import { motion } from 'framer-motion';

const SUGGESTED_PROMPTS = [
  'Recommend 3 dark sci-fi movies from the 80s',
  'Movies like Interstellar but more emotional',
  'Give me 3 comedy movies from the 2000s',
  'Family-friendly adventure movies',
  'Top-rated thrillers, no horror please',
  'Underrated horror films for adults',
];

const EXAMPLES = [
  'Sci-fi movies like Interstellar',
  'Dark thrillers from the 90s',
  'Family movies for a rainy weekend',
  'Underrated horror films',
];

interface SuggestedPromptsProps {
  onSelect: (prompt: string) => void;
}

export default function SuggestedPrompts({ onSelect }: SuggestedPromptsProps) {
  return (
    <div className="mx-auto max-w-[560px] text-center">
      <motion.div
        className="mb-6 flex items-center justify-center gap-2"
        initial={{ opacity: 0, y: -8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <Sparkles className="h-5 w-5 text-red-400" />
        <h2 className="text-[32px] font-bold tracking-tight text-white md:text-[40px]">
          Find movies using{' '}
          <span className="bg-gradient-to-r from-white to-zinc-400 bg-clip-text text-transparent">
            natural language
          </span>
        </h2>
      </motion.div>

      <motion.p
        className="mb-8 text-[17px] leading-relaxed text-zinc-400"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
      >
        Ask for anything. Be as specific or broad as you like.
      </motion.p>

      <motion.div
        className="mb-8 text-left"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.25 }}
      >
        <p className="mb-3 text-sm font-medium text-zinc-500">For example:</p>
        <ul className="space-y-2">
          {EXAMPLES.map((example, i) => (
            <li key={i} className="flex items-start gap-3 text-[15px] text-zinc-400">
              <span className="mt-2 h-1 w-1 flex-shrink-0 rounded-full bg-zinc-600" />
              {example}
            </li>
          ))}
        </ul>
      </motion.div>

      <motion.div
        className="flex flex-wrap justify-center gap-2"
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        {SUGGESTED_PROMPTS.map((prompt, i) => (
          <motion.button
            key={prompt}
            onClick={() => onSelect(prompt)}
            className="rounded-full border border-white/[0.06] bg-white/[0.03] px-4 py-2 text-[14px] text-zinc-300 transition-all hover:bg-white/[0.06] hover:text-white hover:border-white/10"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.35 + i * 0.05 }}
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
