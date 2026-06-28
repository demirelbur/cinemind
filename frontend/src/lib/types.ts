export interface MovieRecommendation {
  id: string;
  title: string;
  posterUrl: string | null;
  backdropUrl: string | null;
  year: number;
  runtimeMinutes?: number;
  genres: string[];
  certification?: string;
  imdbRating: number;
  imdbVotes?: number;
  matchScore: number;
  synopsis: string;
  reason: string;
  tags?: string[];
  director?: { name: string };
  leadActor?: { name: string };
  audience?: string;
  trailerUrl?: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  movies?: MovieRecommendation[];
}
