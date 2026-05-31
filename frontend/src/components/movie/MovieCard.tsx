'use client';

import { ChevronDown, ExternalLink, Film, Play, Plus } from 'lucide-react';
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

import type { MovieRecommendation } from '@/lib/types';

import ImdbRating from '@/components/movie/ImdbRating';
import MatchScoreRing from '@/components/movie/MatchScoreRing';
import WhyItMatches from '@/components/movie/WhyItMatches';

interface MovieCardProps {
  movie: MovieRecommendation;
  index: number;
}

function getTopLabel(i: number): string {
  if (i === 0) return 'Best Match';
  if (i === 1) return 'Also Great';
  return 'Recommended';
}

function getInitials(name: string): string {
  return name
    .split(' ')
    .map((w) => w[0])
    .join('')
    .slice(0, 2)
    .toUpperCase();
}

function truncateSynopsis(text: string, maxWords: number): string {
  const words = text.split(' ');
  if (words.length <= maxWords) return text;
  return words.slice(0, maxWords).join(' ') + '…';
}

export default function MovieCard({ movie, index }: MovieCardProps) {
  const [expanded, setExpanded] = useState(false);
  const isPoster = !!movie.posterUrl;
  const label = getTopLabel(index);
  const synopsisHalf = truncateSynopsis(movie.synopsis, 40);
  const fullSynopsis = movie.synopsis.length > 80;

  return (
    <motion.article
      className="group relative overflow-hidden rounded-[24px] border border-white/[0.08] backdrop-blur-sm transition-all duration-300 hover:-translate-y-1 hover:border-white/[0.15] hover:shadow-[0_20px_60px_rgba(0,0,0,0.6)]"
      style={{
        background:
          'linear-gradient(145deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01))',
      }}
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: index * 0.12 }}
    >
      <div className="flex flex-col gap-0 lg:flex-row">
        {/* Poster — larger, ~38% */}
        <div className="relative lg:w-[38%] lg:min-w-[220px]">
          <div className="group/poster relative aspect-[2/3] overflow-hidden rounded-l-[24px] lg:rounded-l-[24px] lg:rounded-tr-none">
            {isPoster ? (
              <motion.img
                src={movie.posterUrl!}
                alt={`Poster for ${movie.title}`}
                className="h-full w-full object-cover transition-transform duration-500 group-hover/poster:scale-105"
                loading="lazy"
              />
            ) : (
              <div className="flex h-full flex-col items-center justify-center gap-3 bg-gradient-to-b from-[#1A1A1E] to-[#101013] pb-4 pt-20 text-zinc-500">
                <Film className="h-10 w-10 opacity-20" />
                <span className="text-5xl font-bold tracking-tight text-zinc-600">{movie.year}</span>
                <span className="mt-1 rounded-full bg-white/5 px-3 py-1 text-[12px] text-zinc-500">
                  {movie.genres[0]}
                </span>
              </div>
            )}
            {/* Top label overlay — subtle */}
            <div className="absolute left-3 top-3">
              <span className="rounded-full bg-black/40 px-2.5 py-0.5 text-[10px] font-medium uppercase tracking-wider text-zinc-300 backdrop-blur-md">
                {label}
              </span>
            </div>
          </div>
        </div>

        {/* Content area — ~62% */}
        <div className="flex flex-1 flex-col gap-5 p-6 lg:p-7">
          {/* Title + score row */}
          <div className="flex items-start justify-between gap-6">
            <div className="space-y-2.5">
              <h3 className="text-2xl font-bold leading-tight tracking-tight text-white md:text-[28px]">
                {movie.title}
              </h3>
              <div className="flex flex-wrap items-center gap-2 text-[14px] text-zinc-400">
                <span>{movie.year}</span>
                {movie.genres.map((g) => (
                  <span key={g}>
                    <span className="text-zinc-600">·</span>
                    <span>{g}</span>
                  </span>
                ))}
                {movie.duration !== 'N/A' && (
                  <span>
                    <span className="text-zinc-600">·</span>
                    <span>{movie.duration}</span>
                  </span>
                )}
                {movie.certification && (
                  <span className="rounded border border-zinc-700 px-1.5 py-0.5 text-[12px] text-zinc-400">
                    {movie.certification}
                  </span>
                )}
              </div>
              <div>
                <ImdbRating rating={movie.imdbRating} votes={movie.imdbVotes} />
              </div>
            </div>
            <MatchScoreRing score={movie.matchScore} />
          </div>

          {/* Why it matches */}
          <WhyItMatches
            reason={movie.reason}
            details={movie.matchDetails}
            genre={movie.genres[0]}
            decade={`${Math.floor(movie.year / 10) * 10}s`}
            audience={movie.audience}
          />

          {/* Synopsis */}
          <p className="text-[15px] leading-relaxed text-zinc-300">
            {expanded || !fullSynopsis ? movie.synopsis : synopsisHalf}
            {fullSynopsis && !expanded && (
              <button
                onClick={() => setExpanded(true)}
                className="ml-1 text-zinc-400 underline underline-offset-2 hover:text-white"
              >
                more
              </button>
            )}
          </p>

          {/* People row */}
          <div className="flex flex-wrap items-center gap-5">
            {movie.director && (
              <div className="flex items-center gap-2.5">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-zinc-700 to-zinc-800 text-[11px] font-bold text-zinc-300">
                  {getInitials(movie.director.name)}
                </div>
                <div>
                  <p className="text-[11px] text-zinc-500">Director</p>
                  <p className="text-[14px] font-medium text-zinc-300">
                    {movie.director.name}
                  </p>
                </div>
              </div>
            )}
            {movie.leadActor && (
              <div className="flex items-center gap-2.5">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-zinc-700 to-zinc-800 text-[11px] font-bold text-zinc-300">
                  {getInitials(movie.leadActor.name)}
                </div>
                <div>
                  <p className="text-[11px] text-zinc-500">Lead</p>
                  <p className="text-[14px] font-medium text-zinc-300">
                    {movie.leadActor.name}
                  </p>
                </div>
              </div>
            )}
            {movie.audience && (
              <span className="rounded-full bg-white/5 px-3 py-1 text-[12px] font-medium text-zinc-400">
                {movie.audience}
              </span>
            )}
          </div>

          {/* Action bar */}
          <div className="flex flex-wrap items-center gap-3 pt-2">
            <button
              className="inline-flex items-center gap-2 rounded-xl bg-red-600 px-5 py-2.5 text-[14px] font-medium text-white shadow-lg shadow-red-600/20 transition-all hover:bg-red-500 hover:shadow-red-500/30"
              aria-label={`Watch trailer for ${movie.title}`}
            >
              <Play className="h-4 w-4 fill-white" />
              Watch Trailer
            </button>
            <button
              className="inline-flex items-center gap-2 rounded-xl border border-white/[0.06] bg-white/[0.03] px-4 py-2.5 text-[14px] font-medium text-zinc-300 transition-all hover:bg-white/[0.06] hover:text-white"
              aria-label={`Add ${movie.title} to watchlist`}
            >
              <Plus className="h-4 w-4" />
              Watchlist
            </button>
            <button
              className="inline-flex items-center gap-1.5 rounded-xl px-4 py-2.5 text-[14px] font-medium text-zinc-400 transition-colors hover:text-white"
              aria-label={`View details for ${movie.title}`}
            >
              Details
              <ExternalLink className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      </div>
    </motion.article>
  );
}
