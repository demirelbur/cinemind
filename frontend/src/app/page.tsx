'use client';

import { useCallback } from 'react';
import { AlertTriangle } from 'lucide-react';
import { motion } from 'framer-motion';

import AppHeader from '@/components/layout/AppHeader';
import BackgroundGlow from '@/components/layout/BackgroundGlow';
import ChatInput from '@/components/chat/ChatInput';
import SuggestedPrompts from '@/components/chat/SuggestedPrompts';
import MovieCard from '@/components/movie/MovieCard';
import SearchLoading from '@/components/search/SearchLoading';
import { sendChatMessage } from '@/lib/api';
import { useChatStore } from '@/store/useChatStore';

export default function CineMindApp() {
  const { messages, isLoading, error, addMessage, setLoading, setError } =
    useChatStore();

  const handleSubmit = useCallback(
    async (message: string) => {
      addMessage({ id: crypto.randomUUID(), role: 'user', content: message });
      setLoading(true);
      setError(null);

      try {
        const { movies } = await sendChatMessage(message);
        addMessage({
          id: crypto.randomUUID(),
          role: 'assistant',
          content: '',
          movies,
        });
      } catch (err) {
        setError(
          err instanceof Error ? err.message : 'Something went wrong. Please try again.',
        );
      } finally {
        setLoading(false);
      }
    },
    [addMessage, setLoading, setError],
  );

  const lastUserMsg = [...messages].reverse().find((m) => m.role === 'user');
  const latestResult = [...messages].reverse().find(
    (m) => m.role === 'assistant' && m.movies?.length,
  );

  // Check if the current query was answered with zero results
  const latestAssistant = lastUserMsg
    ? messages.slice(messages.indexOf(lastUserMsg)).find((m) => m.role === 'assistant')
    : null;
  const currentQueryEmpty = latestAssistant && (!latestAssistant.movies || !latestAssistant.movies.length);

  const hasResults =
    !isLoading && !error && lastUserMsg && latestResult && latestResult.movies?.length && !currentQueryEmpty;

  const showEmptyState = !messages.length && !isLoading;

  return (
    <div className="noise-overlay relative flex min-h-screen flex-col">
      <BackgroundGlow />

      <div className="relative z-10 mx-auto flex w-full max-w-[860px] flex-1 flex-col px-4 sm:px-6">
        <div className="pt-6 md:pt-10">
          <AppHeader />
        </div>

        {error && (
          <motion.div
            className="mb-6 flex items-start gap-3 rounded-2xl border border-red-500/20 bg-red-500/[0.06] p-4 text-sm text-red-300"
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            role="alert"
          >
            <AlertTriangle className="mt-0.5 h-5 w-5 flex-shrink-0" />
            <div>
              <p className="font-medium">Something went wrong while finding movies.</p>
              <p className="mt-1 text-zinc-400">{error}</p>
              <button
                onClick={() => setError(null)}
                className="mt-2 text-sm underline underline-offset-2 hover:text-zinc-300"
              >
                Dismiss
              </button>
            </div>
          </motion.div>
        )}

        {/* Empty state */}
        {showEmptyState && (
          <div className="flex flex-1 flex-col items-center justify-center py-20">
            <SuggestedPrompts onSelect={handleSubmit} />
          </div>
        )}

        {/* Latest query */}
        {!showEmptyState && lastUserMsg && (
          <motion.div
            key={`q-${lastUserMsg.id}`}
            className="mb-4"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <p className="text-[12px] font-medium uppercase tracking-wider text-zinc-500">
              You asked
            </p>
            <p className="mt-1 text-lg font-medium text-white">"{lastUserMsg.content}"</p>
          </motion.div>
        )}

        {/* Results */}
        {!showEmptyState && (
          <>
            {hasResults && (
              <motion.div
                key={latestResult!.id}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.06 }}
              >
                {/* Result count header */}
                <div className="mb-5">
                  <h4 className="mb-1.5 text-[15px] font-semibold text-zinc-300">
                    {latestResult.movies!.length} result{latestResult.movies!.length === 1 ? '' : 's'} found
                  </h4>
                  <p className="text-[14px] leading-relaxed text-zinc-400">
                    Ranked by relevance to your query, critical reception, and match confidence.
                  </p>
                </div>

                {/* Movie cards */}
                <div className="space-y-2.5">
                  {latestResult.movies!.map((movie, idx) => (
                    <MovieCard key={movie.id + idx} movie={movie} index={idx} />
                  ))}
                </div>
              </motion.div>
            )}

            {/* Loading state */}
            {isLoading && lastUserMsg && <SearchLoading />}

            {/* No results state */}
            {!isLoading && lastUserMsg && currentQueryEmpty && (
              <motion.div
                className="rounded-2xl border border-white/[0.06] bg-zinc-900/30 p-8 text-center"
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
              >
                <p className="text-[15px] font-medium text-zinc-300">
                  No matching movies found
                </p>
                <p className="mt-1.5 text-[14px] text-zinc-500">
                  Try rephrasing your query or broadening the search.
                </p>
              </motion.div>
            )}
          </>
        )}

        {/* Bottom spacer for sticky input */}
        <div className="h-44" />
      </div>

      {/* Sticky bottom input */}
      <div className="fixed bottom-0 left-0 right-0 z-20 pb-5 pt-5">
        <div className="absolute inset-x-0 bottom-0 h-20 bg-gradient-to-t from-[#08080A] to-transparent" />
        <div className="relative">
          <ChatInput onSubmit={handleSubmit} isLoading={isLoading} />
        </div>
      </div>
    </div>
  );
}

