'use client';

import { Film, Play, Star, User, Sparkles, Bookmark } from 'lucide-react';
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
  const hasBackdrop = !!movie.backdropUrl;
  const synopsisLong = movie.synopsis.length > 100;
  const synopsisShort = truncateSynopsis(movie.synopsis, 14);

  const displayTags = movie.tags?.filter(Boolean).slice(0, 4) || [];

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
      {hasBackdrop && (
        <div
          className="pointer-events-none absolute inset-0"
          style={{
            backgroundImage: `url(${movie.backdropUrl})`,
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            opacity: 0.06,
            filter: 'blur(2px)',
          }}
        />
      )}

      <div className="relative">
        {!hasPoster && (
          <ContentSection
            movie={movie}
            synopsisExpanded={synopsisExpanded}
            setSynopsisExpanded={setSynopsisExpanded}
            synopsisLong={synopsisLong}
            synopsisShort={synopsisShort}
            displayTags={displayTags}
          />
        )}

        {hasPoster && (
          <div className="flex flex-col gap-0 lg:flex-row">
            <div className="relative w-full lg:w-[28%] lg:min-w-[160px]">
              <div className="group/poster relative aspect-[2/3] overflow-hidden rounded-l-xl lg:rounded-tr-none">
                <motion.img
                  src={movie.posterUrl!}
                  alt={`Poster for ${movie.title}`}
                  className="h-full w-full object-cover transition-transform duration-500 group-hover/poster:scale-105"
                  loading="lazy"
                />
              </div>
            </div>

            <ContentSection
              movie={movie}
              synopsisExpanded={synopsisExpanded}
              setSynopsisExpanded={setSynopsisExpanded}
              synopsisLong={synopsisLong}
              synopsisShort={synopsisShort}
              displayTags={displayTags}
            />
          </div>
        )}
      </div>
    </motion.article>
  );
}

interface ContentSectionProps {
  movie: MovieRecommendation;
  synopsisExpanded: boolean;
  setSynopsisExpanded: (v: boolean) => void;
  synopsisLong: boolean;
  synopsisShort: string;
  displayTags: string[];
}

function ContentSection({
  movie,
  synopsisExpanded,
  setSynopsisExpanded,
  synopsisLong,
  synopsisShort,
  displayTags,
}: ContentSectionProps) {
  return (
    <div className="flex flex-1 flex-col gap-3 p-4">
      {/* Title + score */}
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 space-y-1">
          <h3 className="truncate text-[17px] font-bold leading-tight tracking-tight text-white md:text-[19px]">
            {movie.title}
          </h3>
          <div className="flex flex-wrap items-center gap-1.5 text-[12px] text-zinc-400">
            <span>{movie.year}</span>
            {movie.genres.map((g) => (
              <span key={g}>
                <span className="text-zinc-600">·</span>
                <span>{g}</span>
              </span>
            ))}
            {movie.duration !== 'N/A' && (
              <span>
                <span className="text-zinc-600">·</span> {movie.duration}
              </span>
            )}
            {movie.certification && (
              <span className="rounded border border-zinc-700 px-1.5 py-0.5 text-[11px] text-zinc-400">
                {movie.certification}
              </span>
            )}
          </div>
          <ImdbRating rating={movie.imdbRating} votes={movie.imdbVotes} />
        </div>
        <MatchScoreBadge score={movie.matchScore} />
      </div>

      {/* Editorial tags — more prominent */}
      {displayTags.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {displayTags.map((tag) => (
            <span
              key={tag}
              className="rounded-full border border-white/[0.14] bg-white/[0.07] px-2.5 py-0.5 text-[11px] font-semibold text-zinc-200"
            >
              {tag}
            </span>
          ))}
        </div>
      )}

      {/* Section 1: Why It Matches */}
      <div>
        <div className="mb-1.5 flex items-center gap-1.5">
          <Sparkles className="h-3.5 w-3.5 text-amber-400/80" />
          <span className="text-[11px] font-semibold uppercase tracking-wider text-zinc-500">
            Why it matches
          </span>
        </div>
        <WhyItMatches reason={movie.reason} />
      </div>

      {/* Section 2: Story */}
      {movie.synopsis && (
        <div>
          <div className="mb-1.5 flex items-center gap-1.5">
            <Bookmark className="h-3.5 w-3.5 text-zinc-500" />
            <span className="text-[11px] font-semibold uppercase tracking-wider text-zinc-500">
              Story
            </span>
          </div>
          <div className="rounded-xl bg-zinc-900/40 p-3">
            <p className="text-[12px] leading-snug text-zinc-300">
              {synopsisExpanded || !synopsisLong ? movie.synopsis : synopsisShort}
            </p>
            {synopsisLong && !synopsisExpanded && (
              <button
                onClick={() => setSynopsisExpanded(true)}
                className="mt-1 text-[11px] text-zinc-500 underline underline-offset-2 hover:text-zinc-300"
              >
                Read more
              </button>
            )}
          </div>
        </div>
      )}

      {/* Credits with icons */}
      <div className="flex flex-wrap items-center gap-3">
        {movie.director && (
          <span className="flex items-center gap-1.5 text-[12px] text-zinc-400">
            <Film className="h-3 w-3 text-zinc-500" />
            <span className="text-zinc-300">{movie.director.name}</span>
          </span>
        )}
        {movie.leadActor && (
          <span className="flex items-center gap-1.5 text-[12px] text-zinc-400">
            <Star className="h-3 w-3 text-zinc-500" />
            <span className="text-zinc-300">{movie.leadActor.name}</span>
          </span>
        )}
        {movie.audience && (
          <span className="flex items-center gap-1.5 text-[12px] text-zinc-400">
            <User className="h-3 w-3 text-zinc-500" />
            <span className="text-zinc-300">{movie.audience}</span>
          </span>
        )}
      </div>

      {/* Action bar */}
      <div className="flex flex-wrap items-center gap-2 pt-0.5">
        {movie.trailerUrl ? (
          <a
            href={movie.trailerUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 rounded-lg bg-red-600/90 px-3.5 py-1.5 text-[12px] font-medium text-white shadow-md shadow-red-600/15 transition-all hover:bg-red-500"
          >
            <Play className="h-3 w-3 fill-white" />
            Trailer
          </a>
        ) : (
          <button className="inline-flex items-center gap-1.5 rounded-lg bg-red-600/90 px-3.5 py-1.5 text-[12px] font-medium text-white shadow-md shadow-red-600/15 transition-all hover:bg-red-500">
            <Play className="h-3 w-3 fill-white" />
            Trailer
          </button>
        )}
      </div>
    </div>
  );
}
