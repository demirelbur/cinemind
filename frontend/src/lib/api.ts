import axios, { AxiosError } from 'axios';

import type { MovieRecommendation } from '@/lib/types';

// Use relative baseURL so client-side requests always go through the
// Next.js API route handler, which proxies to the CineMind backend.
const client = axios.create({
  baseURL: '/',
  timeout: 60_000,
  headers: { 'Content-Type': 'application/json' },
});

export async function sendChatMessage(message: string): Promise<{
  movies: MovieRecommendation[];
}> {
  try {
    const { data } = await client.post<{ movies: MovieRecommendation[] }>('/api/chat', { message });
    return { movies: data.movies };
  } catch (err) {
    const errorData = err instanceof AxiosError ? err.response?.data : null;
    const detail =
      errorData?.error || errorData?.detail || (err instanceof Error && err.message) || 'Unknown error';
    throw new Error(
      typeof detail === 'string' &&
        (detail.includes('validation error') || detail.includes('Recommendation engine failed'))
        ? 'The recommendation service is having trouble. Please try again with a different query.'
        : typeof detail === 'string'
          ? detail
          : 'Something went wrong while finding movies. Please try again.',
    );
  }
}
