import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  const body = await req.json();
  const message = body?.message || '';

  if (!message || message.length < 3) {
    return NextResponse.json(
      { error: 'Message must be at least 3 characters' },
      { status: 400 },
    );
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
      return NextResponse.json(
        { error: detail.detail || 'Recommendation service error' },
        { status: res.status },
      );
    }

    const data: { query: string; recommendations: Array<{ movie: { title: string; genre: string; year: number; rating: number; synopsis: string; director: string | null; lead_actor: string | null; recommended_for: string | null }; reason: string; match_score: number }> } = await res.json();

    const movies = data.recommendations.map((rec) => ({
      id: rec.movie.title.toLowerCase().replace(/[^\w]+/g, '-'),
      title: rec.movie.title,
      posterUrl: null,
      year: rec.movie.year,
      genre: rec.movie.genre,
      rating: rec.movie.rating,
      synopsis: rec.movie.synopsis,
      director: rec.movie.director,
      lead_actor: rec.movie.lead_actor,
      recommended_for: rec.movie.recommended_for,
      match_score: Math.round(rec.match_score * 100),
      reason: rec.reason,
    }));

    return NextResponse.json({
      answer: `Found ${movies.length} movie${movies.length === 1 ? '' : 's'} matching your request.`,
      movies,
    });
  } catch {
    return NextResponse.json(
      { error: 'Could not reach the recommendation service. Please try again shortly.' },
      { status: 503 },
    );
  }
}
