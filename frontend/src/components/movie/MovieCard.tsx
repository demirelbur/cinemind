'use client';

import { ExternalLink, Film, Play, Plus, Star, User } from 'lucide-react';
import { useState } from 'react';
import { motion } from 'framer-motion';

import type { MovieRecommendation } from '@/lib/types';

import ImdbRating from '@/components/movie/ImdbRating';
import MatchScoreBadge from '@/components/movie/MatchScoreBadge';
import WhyItMatches from '@/components/movie/WhyItMatches';

interface MovieCardProps {
  movie: MovieRecommendation;
  index: number;
}

function truncateSynopsis(text: string, maxWords: number): string {
  const words = text.split(' ');
  if (words.length <= maxWords) return text;
  return words.slice(0, maxWords).join(' ') + '…';
}

export default function MovieCard({ movie, index }: MovieCardProps) {
  const [synopsisExpanded, setSynopsisExpanded] = useState(false);
  const hasPoster = !!movie.posterUrl;
  const synopsisLong = movie.synopsis.length > 100;
  const synopsisShort = truncateSynopsis(movie.synopsis, 14);
  const decade = `${Math.floor(movie.year / 10) * 10}s`;

  return (
    <motion.article
      className="group relative overflow-hidden rounded-2xl border border-white/[0.06] backdrop-blur-sm transition-all duration-300 hover:-translate-y-0.5 hover:border-white/[0.12] hover:shadow-[0_16px_48px_rgba(0,0,0,0.5)]"
      style={{
        background: 'linear-gradient(145deg, rgba(255,255,255,0.025), rgba(255,255,255,0.005))',
      }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, delay: index * 0.08 }}
    >
      {!hasPoster && (
        <div className="flex flex-1 flex-col gap-3 p-5">
          {/* Title + score — same row */}
          <div className="flex items-start justify-between gap-4">
            <div className="min-w-0 space-y-1.5">
              <h3 className="truncate text-xl font-bold leading-tight tracking-tight text-white md:text-[22px]">
                {movie.title}
              </h3>
              <div className="flex flex-wrap items-center gap-1.5 text-[13px] text-zinc-400">
                <span>{movie.year}</span>
                {movie.genres.map((g) => (
                  <span key={g}>
                    <span className="text-zinc-600">·</span>
                    <span>{g}</span>
                  </span>
                ))}
                {movie.duration !== 'N/A' && <span><span className="text-zinc-600">·</span> {movie.duration}</span>}
                {movie.certification && (
                  <span className="rounded border border-zinc-700 px-1.5 py-0.5 text-[11px] text-zinc-400">{movie.certification}</span>
                )}
              </div>
              <ImdbRating rating={movie.imdbRating} votes={movie.imdbVotes} />
            </div>
            <MatchScoreBadge score={movie.matchScore} />
          </div>

          {/* Tags — prominent, near title */}
          {movie.tags && movie.tags.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {movie.tags.map((tag) => (
                <span
                  key={tag}
                  className="rounded-full border border-white/[0.08] bg-white/[0.04] px-2.5 py-0.5 text-[11px] font-medium text-zinc-300"
                >
                  {tag}
                </span>
              ))}
            </div>
          )}

          {/* Why it matches — compressed: chips first, then one-liner */}
          <WhyItMatches
            reason={movie.reason}
            details={movie.matchDetails}
            genre={movie.genres[0]}
            decade={decade}
            audience={movie.audience}
          />

          {/* Synopsis — collapsed to ~2 lines */}
          <p className="text-[13px] leading-relaxed text-zinc-400">
            {synopsisExpanded || !synopsisLong ? movie.synopsis : synopsisShort}
            {synopsisLong && !synopsisExpanded && (
              <button
                onClick={() => setSynopsisExpanded(true)}
                className="ml-0.5 text-[12px] text-zinc-500 underline underline-offset-2 hover:text-zinc-300"
              >
                Read more
              </button>
            )}
          </p>

          {/* People — compact icon-only row */}
          <div className="flex flex-wrap items-center gap-4">
            {movie.director && (
              <span className="flex items-center gap-1.5 text-[13px] text-zinc-400">
                <Film className="h-3.5 w-3.5 text-zinc-500" />
                {movie.director.name}
              </span>
            )}
            {movie.leadActor && (
              <span className="flex items-center gap-1.5 text-[13px] text-zinc-400">
                <Star className="h-3.5 w-3.5 text-zinc-500" />
                {movie.leadActor.name}
              </span>
            )}
            {movie.audience && (
              <span className="flex items-center gap-1.5 text-[13px] text-zinc-400">
                <User className="h-3.5 w-3.5 text-zinc-500" />
                {movie.audience}
              </span>
            )}
          </div>

          {/* Action bar — compact */}
          <div className="flex flex-wrap items-center gap-2 pt-1">
            {movie.trailerUrl ? (
              <a
                href={movie.trailerUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 rounded-lg bg-red-600/90 px-4 py-2 text-[13px] font-medium text-white shadow-md shadow-red-600/15 transition-all hover:bg-red-500"
              >
                <Play className="h-3.5 w-3.5 fill-white" />
                Trailer
              </a>
            ) : (
              <button className="inline-flex items-center gap-1.5 rounded-lg bg-red-600/90 px-4 py-2 text-[13px] font-medium text-white shadow-md shadow-red-600/15 transition-all hover:bg-red-500">
                <Play className="h-3.5 w-3.5 fill-white" />
                Trailer
              </button>
            )}
            <button className="inline-flex items-center gap-1.5 rounded-lg border border-white/[0.06] bg-white/[0.03] px-3 py-2 text-[13px] font-medium text-zinc-400 transition-all hover:bg-white/[0.06] hover:text-white">
              <Plus className="h-3.5 w-3.5" />
              Watchlist
            </button>
            <button className="inline-flex items-center gap-1.5 rounded-lg px-3 py-2 text-[13px] font-medium text-zinc-500 transition-colors hover:text-white">
              Details
              <ExternalLink className="h-3 w-3" />
            </button>
          </div>
        </div>
      )}

      {hasPoster && (
        <div className="flex flex-col gap-0 lg:flex-row">
          {/* Poster — 30% */}
          <div className="relative w-full lg:w-[30%] lg:min-w-[180px]">
            <div className="group/poster relative aspect-[2/3] overflow-hidden rounded-l-xl lg:rounded-tr-none">
              <motion.img
                src={movie.posterUrl!}
                alt={`Poster for ${movie.title}`}
                className="h-full w-full object-cover transition-transform duration-500 group-hover/poster:scale-105"
                loading="lazy"
              />
            </div>
          </div>

          <div className="flex flex-1 flex-col gap-3 p-5">
            {/* Title + score — same row */}
            <div className="flex items-start justify-between gap-4">
              <div className="min-w-0 space-y-1.5">
                <h3 className="truncate text-xl font-bold leading-tight tracking-tight text-white md:text-[22px]">
                  {movie.title}
                </h3>
                <div className="flex flex-wrap items-center gap-1.5 text-[13px] text-zinc-400">
                  <span>{movie.year}</span>
                  {movie.genres.map((g) => (
                    <span key={g}>
                      <span className="text-zinc-600">·</span>
                      <span>{g}</span>
                    </span>
                  ))}
                  {movie.duration !== 'N/A' && <span><span className="text-zinc-600">·</span> {movie.duration}</span>}
                  {movie.certification && (
                    <span className="rounded border border-zinc-700 px-1.5 py-0.5 text-[11px] text-zinc-400">{movie.certification}</span>
                  )}
                </div>
                <ImdbRating rating={movie.imdbRating} votes={movie.imdbVotes} />
              </div>
              <MatchScoreBadge score={movie.matchScore} />
            </div>

            {/* Tags */}
            {movie.tags && movie.tags.length > 0 && (
              <div className="flex flex-wrap gap-1.5">
                {movie.tags.map((tag) => (
                  <span
                    key={tag}
                    className="rounded-full border border-white/[0.08] bg-white/[0.04] px-2.5 py-0.5 text-[11px] font-medium text-zinc-300"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            )}

            {/* Why it matches */}
            <WhyItMatches
              reason={movie.reason}
              details={movie.matchDetails}
              genre={movie.genres[0]}
              decade={decade}
              audience={movie.audience}
            />

            {/* Synopsis */}
            <p className="text-[13px] leading-relaxed text-zinc-400">
              {synopsisExpanded || !synopsisLong ? movie.synopsis : synopsisShort}
              {synopsisLong && !synopsisExpanded && (
                <button
                  onClick={() => setSynopsisExpanded(true)}
                  className="ml-0.5 text-[12px] text-zinc-500 underline underline-offset-2 hover:text-zinc-300"
                >
                  Read more
                </button>
              )}
            </p>

            {/* People */}
            <div className="flex flex-wrap items-center gap-4">
              {movie.director && (
                <span className="flex items-center gap-1.5 text-[13px] text-zinc-400">
                  <Film className="h-3.5 w-3.5 text-zinc-500" />
                  {movie.director.name}
                </span>
              )}
              {movie.leadActor && (
                <span className="flex items-center gap-1.5 text-[13px] text-zinc-400">
                  <Star className="h-3.5 w-3.5 text-zinc-500" />
                  {movie.leadActor.name}
                </span>
              )}
              {movie.audience && (
                <span className="flex items-center gap-1.5 text-[13px] text-zinc-400">
                  <User className="h-3.5 w-3.5 text-zinc-500" />
                  {movie.audience}
                </span>
              )}
            </div>

            {/* Action bar */}
            <div className="flex flex-wrap items-center gap-2 pt-1">
              {movie.trailerUrl ? (
                <a
                  href={movie.trailerUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 rounded-lg bg-red-600/90 px-4 py-2 text-[13px] font-medium text-white shadow-md shadow-red-600/15 transition-all hover:bg-red-500"
                >
                  <Play className="h-3.5 w-3.5 fill-white" />
                  Trailer
                </a>
              ) : (
                <button className="inline-flex items-center gap-1.5 rounded-lg bg-red-600/90 px-4 py-2 text-[13px] font-medium text-white shadow-md shadow-red-600/15 transition-all hover:bg-red-500">
                  <Play className="h-3.5 w-3.5 fill-white" />
                  Trailer
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </motion.article>
  );
}
