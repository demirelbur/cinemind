import type { MovieRecommendation } from '@/lib/types';

export const mockMovies: MovieRecommendation[] = [
  {
    id: 'blade-runner',
    title: 'Blade Runner',
    posterUrl: 'https://image.tmdb.org/t/p/w500/63kGofwxjqF5wBlLZrFypgBpQfS.jpg',
    backdropUrl: 'https://image.tmdb.org/t/p/original/5TZS10drcCoCWwsRMs9OPCV3KU5.jpg',
    year: 1982,
    runtimeMinutes: 117,
    genres: ['Sci-Fi', 'Thriller'],
    certification: 'R',
    imdbRating: 8.1,
    imdbVotes: 820000,
    matchScore: 95,
    synopsis:
      'In a smog-choked dystopian Los Angeles of 2019, blade runner Rick Deckard is called out of retirement to terminate a quartet of replicants who have escaped to Earth seeking their creator for a way to extend their short life spans.',
    reason:
      'You asked for dark sci-fi movies from the 80s. Blade Runner is a defining work of 80s sci-fi, blending neo-noir atmosphere with profound philosophical questions about humanity, memory, and identity.',
    tags: ['Dark', 'Atmospheric', 'Mind-bending', 'Cult Classic'],
    director: {
      name: 'Ridley Scott',
    },
    leadActor: {
      name: 'Harrison Ford',
    },
    audience: 'Adults',
  },
  {
    id: 'empire-strikes-back',
    title: 'The Empire Strikes Back',
    posterUrl: 'https://image.tmdb.org/t/p/w500/nBNZadXqJSdt05SHLqgT0HuC5Gm.jpg',
    backdropUrl: 'https://image.tmdb.org/t/p/original/6pEltKPqa1Qp7q9QKaqXt5E8EEg.jpg',
    year: 1980,
    runtimeMinutes: 124,
    genres: ['Sci-Fi', 'Action', 'Adventure'],
    certification: 'PG',
    imdbRating: 8.7,
    imdbVotes: 1350000,
    matchScore: 88,
    synopsis:
      'The epic saga continues as Luke Skywalker, in hopes of defeating the evil Galactic Empire, learns the ways of the Jedi from aging master Yoda. But Darth Vader is more determined than ever to capture Luke.',
    reason:
      'A cornerstone of 80s sci-fi cinema. This dark turning point in the Skywalker saga raises the stakes and introduces moral ambiguity, matching your request for mature, atmospheric storytelling from the decade.',
    tags: ['Dark', 'Epic', 'Space Opera', 'Classic'],
    director: {
      name: 'Irvin Kershner',
    },
    leadActor: {
      name: 'Mark Hamill',
    },
    audience: 'Teens',
  },
  {
    id: 'back-to-the-future',
    title: 'Back to the Future',
    posterUrl: 'https://image.tmdb.org/t/p/w500/fNOH9f1aA7XRTzl1sAOx9iF553Q.jpg',
    backdropUrl: 'https://image.tmdb.org/t/p/original/x4N74cycZvKu9UPfe7cdhDgmWd7.jpg',
    year: 1985,
    runtimeMinutes: 116,
    genres: ['Sci-Fi', 'Comedy', 'Adventure'],
    certification: 'PG',
    imdbRating: 8.5,
    imdbVotes: 1290000,
    matchScore: 78,
    synopsis:
      'Eighties teenager Marty McFly is accidentally sent back in time to 1955, inadvertently disrupting his parents first meeting. He must repair the damage to history and find his way back to the future with the help of eccentric scientist Doc Brown.',
    reason:
      'Back to the Future is a quintessential 80s sci-fi film that shifted the tone from dark to upbeat without sacrificing creativity in the genre.',
    tags: ['Upbeat', 'Time Travel', 'Adventure', 'Family-Friendly'],
    director: {
      name: 'Robert Zemeckis',
    },
    leadActor: {
      name: 'Michael J. Fox',
    },
    audience: 'Teens',
  },
];
