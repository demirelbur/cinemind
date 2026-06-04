# CineMind — Next.js Frontend

Next.js frontend for the CineMind movie recommendation app.

## Development

```bash
npm install
npm run dev     # http://localhost:3000
npm run build   # production build
```

## Architecture

```
src/
├── app/
│   ├── page.tsx              # main page: empty state, results, loading, errors
│   ├── layout.tsx            # root layout, metadata, system UI font
│   ├── globals.css           # theme tokens, scrollbar, noise texture
│   └── api/chat/route.ts     # proxy to backend — single transformation layer
├── components/
│   ├── chat/
│   │   ├── ChatInput.tsx             # sticky search input
│   │   └── SuggestedPrompts.tsx      # clickable example prompt chips
│   ├── layout/
│   │   ├── AppHeader.tsx             # CineMind logo + subtitle
│   │   └── BackgroundGlow.tsx        # ambient background gradient
│   ├── movie/
│   │   ├── MovieCard.tsx             # recommendation card (poster + info)
│   │   ├── WhyItMatches.tsx          # AI reasoning in elevated container
│   │   ├── ImdbRating.tsx            # star rating with vote count
│   │   └── MatchScoreBadge.tsx       # percentage match score + label
│   └── search/
│       └── SearchLoading.tsx         # progress step indicator (3 steps)
├── lib/
│   ├── api.ts                    # thin HTTP caller (axios)
│   └── types.ts                  # MovieRecommendation, ChatMessage
└── store/
    └── useChatStore.ts           # Zustand store (messages, loading, error)
```

## Data Flow

Frontend → `/api/chat` (Next.js route) → FastAPI `/recommend` → CineMind backend

The proxy route (`api/chat/route.ts`) is the **single transformation layer** — it fetches raw backend JSON, reshapes it into `MovieRecommendation`, and returns it to the client. `lib/api.ts` is a thin HTTP caller with no transformation logic.

## Design Principles

This frontend follows Lean Product Development (LPD) principles. See the project-level [AGENTS.md](../../AGENTS.md) for the full LPD guidelines.

Key rules applied here:

- **One transformation layer** — data is reshaped only in `api/chat/route.ts`
- **No dead code** — unused components, packages, and CSS are deleted immediately
- **No stale state** — error and zero-result states never show previous results
- **Inline before modularizing** — components are extracted only when duplication is painful
- **Ship over polish** — CSS transitions used over heavy animation libraries where possible
