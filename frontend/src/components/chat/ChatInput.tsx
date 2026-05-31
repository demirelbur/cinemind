'use client';

import { useEffect, useRef } from 'react';
import { ArrowUp, Loader2 } from 'lucide-react';
import { motion } from 'framer-motion';

interface ChatInputProps {
  onSubmit: (message: string) => void;
  isLoading: boolean;
}

export default function ChatInput({ onSubmit, isLoading }: ChatInputProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const el = textareaRef.current;
    if (el) {
      el.style.height = 'auto';
      el.style.height = Math.min(el.scrollHeight, 120) + 'px';
    }
  }, [textareaRef.current?.value]);

  const handleSubmit = () => {
    const el = textareaRef.current;
    if (!el || el.value.trim().length < 3) return;
    onSubmit(el.value.trim());
    el.value = '';
    el.style.height = 'auto';
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="mx-auto w-full max-w-[640px] px-4">
      <motion.form
        onSubmit={(e) => {
          e.preventDefault();
          handleSubmit();
        }}
        className="relative rounded-2xl border border-white/[0.08] bg-[#121216] p-0.5 shadow-2xl shadow-black/50 transition-colors focus-within:border-white/15"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="flex items-end gap-2 rounded-2xl bg-white/[0.02] p-3">
          <textarea
            ref={textareaRef}
            placeholder="Try: Recommend 3 dark sci-fi movies from the 80s..."
            disabled={isLoading}
            rows={1}
            onKeyDown={handleKeyDown}
            className="flex-1 resize-none bg-transparent text-[15px] leading-relaxed text-white placeholder:text-zinc-500 outline-none [resize:none] disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={isLoading}
            className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-xl bg-red-600 text-white transition-all hover:bg-red-500 disabled:bg-zinc-700"
            aria-label="Send message"
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <ArrowUp className="h-4 w-4" />
            )}
          </button>
        </div>
      </motion.form>
      <motion.p
        className="mt-2 text-center text-[12px] text-zinc-600"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
      >
        Enter to send · Shift+Enter for new line
      </motion.p>
    </div>
  );
}
