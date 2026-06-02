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

    const data: { query: string; recommendations: Array<{ movie: Record<string, unknown>; reason: string; match_score: number }> } = await res.json();

    const movies = data.recommendations.map((rec) => {
      const m = rec.movie;
      return {
        title: m.title,
        poster_url: m.poster_url || null,
        backdrop_url: m.backdrop_url || null,
        trailer_url: m.trailer_url || null,
        editorial_tags: m.editorial_tags || null,
        vote_count: m.vote_count || null,
        year: m.year,
        genre: m.genre,
        rating: m.rating,
        synopsis: m.synopsis,
        director: m.director,
        lead_actor: m.lead_actor,
        lead_actor_2: m.lead_actor_2 || null,
        lead_actor_3: m.lead_actor_3 || null,
        recommended_for: m.recommended_for,
        match_score: Math.round((rec.match_score as number) * 100),
        reason: rec.reason,
      };
    });

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
