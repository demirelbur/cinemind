'use client';

import { useCallback } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AlertTriangle, Sparkles } from 'lucide-react';
import { motion } from 'framer-motion';

import AppHeader from '@/components/layout/AppHeader';
import BackgroundGlow from '@/components/layout/BackgroundGlow';
import MessageList from '@/components/chat/MessageList';
import ChatInput from '@/components/chat/ChatInput';
import SuggestedPrompts from '@/components/chat/SuggestedPrompts';
import MovieCard from '@/components/movie/MovieCard';
import MovieCardSkeleton from '@/components/movie/MovieCardSkeleton';
import { sendChatMessage } from '@/lib/api';
import { mockMovies } from '@/lib/mockMovies';
import { useChatStore } from '@/store/useChatStore';

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

function CineMindApp() {
  const { messages, isLoading, error, addMessage, setLoading, setError } =
    useChatStore();

  const handleSubmit = useCallback(
    async (message: string) => {
      addMessage({ id: crypto.randomUUID(), role: 'user', content: message });
      setLoading(true);
      setError(null);

      try {
        const useMock = process.env.NEXT_PUBLIC_USE_MOCK === 'true';

        if (useMock) {
          await new Promise((r) => setTimeout(r, 1500));
          addMessage({
            id: crypto.randomUUID(),
            role: 'assistant',
            content:
              "Based on your request, I prioritized critically acclaimed titles with strong audience appeal and cultural impact.",
            movies: mockMovies,
          });
        } else {
          const { movies, answer } = await sendChatMessage(message);
          addMessage({
            id: crypto.randomUUID(),
            role: 'assistant',
            content: answer,
            movies,
          });
        }
      } catch (err) {
        const msg =
          err instanceof Error ? err.message : 'Something went wrong. Please try again.';
        setError(msg);
      } finally {
        setLoading(false);
      }
    },
    [addMessage, setLoading, setError],
  );

  const lastUserMsg = messages.find((m) => m.role === 'user');
  const latestResult = [...messages].reverse().find((m) => m.role === 'assistant' && m.movies?.length);
  const showEmptyState = messages.filter((m) => m.role === 'user').length === 0 && !isLoading;

  return (
    <div className="noise-overlay relative flex min-h-screen flex-col">
      <BackgroundGlow />

      <div className="relative z-10 mx-auto flex w-full max-w-[960px] flex-1 flex-col px-4 pb-64 pt-4 sm:px-6 md:pt-8">
        <AppHeader />

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

        {/* Empty state hero */}
        {showEmptyState && (
          <div className="flex flex-1 flex-col items-center justify-center py-20">
            <SuggestedPrompts onSelect={handleSubmit} />
          </div>
        )}

        <MessageList messages={messages} isLoading={isLoading} />

        {/* AI Summary + Movie Cards */}
        {!showEmptyState && (
          <>
            {/* AI Recommendation Summary + Movie Cards — keyed on latestResult.id
                so Framer Motion re-animates on each new search */}
            {!isLoading && lastUserMsg && latestResult && latestResult.movies && (
              <motion.div
                key={latestResult.id}
                className="mt-4"
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
              >
                <div className="mb-8">
                  <div className="mb-3 flex items-center gap-2">
                    <Sparkles className="h-4 w-4 text-red-400" />
                    <h4 className="text-[14px] font-semibold text-zinc-400">
                      Based on your request
                    </h4>
                  </div>
                  <blockquote className="rounded-2xl border border-white/[0.06] bg-white/[0.02] p-5">
                    <p className="text-[15px] leading-relaxed text-zinc-300">
                      "{latestResult.content}"
                    </p>
                  </blockquote>
                </div>

                <div className="space-y-6">
                  {latestResult.movies.map((movie, idx) => (
                    <MovieCard key={movie.id + idx} movie={movie} index={idx} />
                  ))}
                </div>
              </motion.div>
            )}

            {/* Loading skeletons — show when loading, hide old cards */}
            {isLoading && lastUserMsg && (
              <div className="space-y-6 pt-4">
                <MovieCardSkeleton index={0} />
                <MovieCardSkeleton index={1} />
                <MovieCardSkeleton index={2} />
              </div>
            )}
          </>
        )}
      </div>

      {/* Sticky bottom input */}
      <div className="fixed bottom-0 left-0 right-0 z-20 pb-8 pt-8">
        <div className="absolute inset-x-0 bottom-0 h-24 bg-gradient-to-t from-[#08080A] to-transparent" />
        <div className="relative">
          <ChatInput onSubmit={handleSubmit} isLoading={isLoading} />
        </div>
      </div>
    </div>
  );
}

export default function Page() {
  return (
    <QueryClientProvider client={queryClient}>
      <CineMindApp />
    </QueryClientProvider>
  );
}
