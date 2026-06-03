'use client';

import { useCallback } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AlertTriangle } from 'lucide-react';
import { motion } from 'framer-motion';

import AppHeader from '@/components/layout/AppHeader';
import BackgroundGlow from '@/components/layout/BackgroundGlow';
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

function buildSummary(query: string, count: number): { header: string; body: string } {
  const q = query.toLowerCase();

  if (q.includes('dark') && q.includes('sci-fi')) {
    return {
      header: `Why these ${count} picks?`,
      body: 'You asked for dark science fiction films. I prioritized atmospheric, moody titles with strong critical reception and themes of existential dread, dystopian settings, or psychological unease.',
    };
  }
  if (q.includes('comedy')) {
    return {
      header: `Why these ${count} picks?`,
      body: 'You asked for comedies. I selected well-reviewed films with varied humor styles — from witty satire to heartfelt stories — focusing on broad audience appeal and standout performances.',
    };
  }
  if (q.includes('horror')) {
    return {
      header: `Why these ${count} picks?`,
      body: 'You asked for horror films. I chose titles that favor atmosphere and dread over cheap jumpscares, prioritizing films with lasting impact and distinctive storytelling.',
    };
  }
  if (q.includes('action')) {
    return {
      header: `Why these ${count} picks?`,
      body: 'You asked for action films. I prioritized high-energy picks with lasting cultural impact and memorable set pieces, balancing mainstream appeal with standout quality.',
    };
  }
  if (q.includes('family')) {
    return {
      header: `Why these ${count} picks?`,
      body: 'You asked for family-friendly picks. I chose warm, engaging films with broad appeal, focusing on stories that resonate across ages while maintaining quality.',
    };
  }
  if (q.includes('underrated')) {
    return {
      header: `Why these ${count} picks?`,
      body: `You asked for underrated films. Less mainstream titles were ranked higher than popular blockbusters, prioritizing critical reception over box office numbers.`,
    };
  }

  // Default
  const genre = q.includes('sci-fi') || q.includes('science fiction') ? 'science fiction' : q.includes('thriller') ? 'thrillers' : q.includes('drama') ? 'dramas' : 'films';
  return {
    header: `Why these ${count} picks?`,
    body: `You asked for ${genre}. I selected critically acclaimed titles that align with your request, ranked by relevance to your query and overall quality.`,
  };
}

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
            content: JSON.stringify(buildSummary(message, mockMovies.length)),
            movies: mockMovies,
          });
        } else {
          const { movies, answer } = await sendChatMessage(message);
          const summary = buildSummary(message, movies.length);
          addMessage({
            id: crypto.randomUUID(),
            role: 'assistant',
            content: JSON.stringify(summary),
            movies,
          });
        }
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
  const hasResults =
    !isLoading && lastUserMsg && latestResult && latestResult.movies?.length;

  // Parse summary from assistant content
  let summary: { header: string; body: string } | null = null;
  if (latestResult) {
    try {
      summary = JSON.parse(latestResult.content);
    } catch {
      // If not JSON, use it as the body
      summary = { header: 'Based on your request', body: latestResult.content };
    }
  }

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
            {hasResults && summary && (
              <motion.div
                key={latestResult!.id}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.06 }}
              >
                {/* AI ranking explanation */}
                <div className="mb-5">
                  <h4 className="mb-1.5 text-[15px] font-semibold text-zinc-300">
                    {summary.header}
                  </h4>
                  <p className="text-[14px] leading-relaxed text-zinc-400">{summary.body}</p>
                </div>

                {/* Movie cards */}
                <div className="space-y-2.5">
                  {latestResult.movies!.map((movie, idx) => (
                    <MovieCard key={movie.id + idx} movie={movie} index={idx} />
                  ))}
                </div>
              </motion.div>
            )}

            {/* Loading skeletons */}
            {isLoading && lastUserMsg && (
              <div className="space-y-3">
                <MovieCardSkeleton index={0} />
                <MovieCardSkeleton index={1} />
                <MovieCardSkeleton index={2} />
              </div>
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

export default function Page() {
  return (
    <QueryClientProvider client={queryClient}>
      <CineMindApp />
    </QueryClientProvider>
  );
}
