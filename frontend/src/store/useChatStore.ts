import { create } from 'zustand';

import { ChatMessage, MovieRecommendation } from '@/lib/types';

type ChatState = {
  messages: ChatMessage[];
  movies: MovieRecommendation[];
  isLoading: boolean;
  error: string | null;
  addMessage: (msg: ChatMessage) => void;
  setMovies: (movies: MovieRecommendation[]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearMovies: () => void;
  clearMessages: () => void;
};

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  movies: [],
  isLoading: false,
  error: null,

  addMessage: (msg) =>
    set((state) => ({
      messages: [...state.messages, msg],
    })),

  setMovies: (movies) => set({ movies }),

  setLoading: (loading) => set({ isLoading: loading }),

  setError: (error) => set({ error }),

  clearMovies: () => set({ movies: [] }),

  clearMessages: () => set({ messages: [] }),
}));
