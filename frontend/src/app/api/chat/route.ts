import { NextRequest, NextResponse } from 'next/server';

type MovieRecord = Record<string, unknown>;

interface MovieRecommendation {
  id: string;
  title: string;
  posterUrl: string | null;
  backdropUrl: string | null;
  year: number;
  genres: string[];
  certification?: string;
  imdbRating: number;
  imdbVotes?: number;
  matchScore: number;
  similarity?: number;
  synopsis: string;
  reason: string;
  tags?: string[];
  matchDetails: {
    genreMatch: boolean;
    decadeMatch: boolean;
    audienceFit: boolean;
    similarity: boolean;
  };
  director?: { name: string };
  leadActor?: { name: string };
  audience?: string;
  trailerUrl?: string;
}

function slugify(text: string): string {
  return text.toLowerCase().replace(/[^\w\s-]/g, '').replace(/\s+/g, '-').replace(/-+/g, '-').trim();
}

function toMovie(rec: { movie: MovieRecord; reason: string; match_score: number }, index: number): MovieRecommendation {
  const m = rec.movie;
  const baseScore = Math.round(rec.match_score * 100);
  const score = Math.max(0, Math.min(100, baseScore - index * 3));

  const actors = [m.lead_actor, m.lead_actor_2, m.lead_actor_3].filter(Boolean) as string[];

  return {
    id: slugify(m.title as string),
    title: m.title as string,
    posterUrl: (m.poster_url as string | null) || null,
    backdropUrl: (m.backdrop_url as string | null) || null,
    year: m.year as number,
    genres: (m.genre ? [m.genre] : []) as string[],
    imdbRating: m.rating as number,
    imdbVotes: (m.vote_count as number) || undefined,
    matchScore: score,
    similarity: rec.match_score,
    synopsis: m.synopsis as string,
    reason: rec.reason,
    tags: ((m.editorial_tags as string[]) || []).slice(0, 4),
    matchDetails: {
      genreMatch: true,
      decadeMatch: true,
      audienceFit: !!m.recommended_for,
      similarity: rec.match_score > 0.6,
    },
    director: (m.director as string | null) ? { name: m.director as string } : undefined,
    leadActor: actors[0] ? { name: actors[0] } : undefined,
    audience: (m.recommended_for as string) || undefined,
    trailerUrl: (m.trailer_url as string) || undefined,
  };
}

export async function POST(req: NextRequest) {
  const body = await req.json();
  const message = body?.message || '';

  if (!message || message.length < 3) {
    return NextResponse.json({ error: 'Message must be at least 3 characters' }, { status: 400 });
  }

  const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

  try {
    const res = await fetch(`${apiBase}/recommend`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: message }),
    });

    if (!res.ok) {
      const detail = await res.json().catch(() => ({}));
      return NextResponse.json({ error: detail.detail || 'Recommendation service error' }, { status: res.status });
    }

    const data = await res.json();
    const recommendations = (data.recommendations || [
      { movie: {}, reason: '', match_score: 0 },
    ]) as Array<{ movie: MovieRecord; reason: string; match_score: number }>;

    const movies: MovieRecommendation[] = recommendations.map((rec, i) => toMovie(rec, i));

    return NextResponse.json({ movies });
  } catch {
    return NextResponse.json(
      { error: 'Could not reach the recommendation service. Please try again shortly.' },
      { status: 503 },
    );
  }
}
