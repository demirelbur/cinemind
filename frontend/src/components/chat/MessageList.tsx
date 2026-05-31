'use client';

import { User } from 'lucide-react';
import { motion } from 'framer-motion';

import type { ChatMessage } from '@/lib/types';

interface MessageListProps {
  messages: ChatMessage[];
  isLoading: boolean;
}

export default function MessageList({ messages }: MessageListProps) {
  // Search model: only show the most recent user query as context
  // Assistant text and movie cards are rendered by the parent
  const lastUserMsg = [...messages].reverse().find((m) => m.role === 'user');

  if (!lastUserMsg) return null;

  return (
    <motion.div
      className="flex justify-end"
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="flex max-w-[75%] items-end gap-3">
        <div className="rounded-2xl rounded-br-md bg-red-600 px-4 py-3 text-[15px] leading-relaxed text-white">
          {lastUserMsg.content}
        </div>
        <div className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-red-500/20">
          <User className="h-3.5 w-3.5 text-red-400" />
        </div>
      </div>
    </motion.div>
  );
}
