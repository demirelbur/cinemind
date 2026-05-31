'use client';

import { motion } from 'framer-motion';

import { Skeleton } from '@/components/ui/skeleton';

export default function MovieCardSkeleton({ index = 0 }: { index?: number }) {
  return (
    <motion.article
      className="overflow-hidden rounded-[24px] border border-white/[0.06]"
      style={{
        background:
          'linear-gradient(145deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01))',
      }}
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.12, duration: 0.4 }}
    >
      <div className="flex flex-col lg:flex-row">
        {/* Poster */}
        <div className="lg:w-[38%] lg:min-w-[220px]">
          <div className="aspect-[2/3] bg-zinc-900">
            <Skeleton className="h-full w-full rounded-none" />
          </div>
        </div>
        {/* Content */}
        <div className="flex flex-1 flex-col gap-5 p-6 lg:p-7">
          <div className="flex items-start justify-between">
            <div className="space-y-3">
              <Skeleton className="h-8 w-56" />
              <Skeleton className="h-4 w-36" />
              <Skeleton className="h-6 w-28" />
            </div>
            <Skeleton className="h-14 w-14 rounded-full" />
          </div>
          <Skeleton className="h-24 w-full rounded-2xl" />
          <div className="space-y-2">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-4/5" />
          </div>
          <div className="flex items-center gap-5">
            <div className="flex items-center gap-2.5">
              <Skeleton className="h-8 w-8 rounded-full" />
              <Skeleton className="h-8 w-20" />
            </div>
            <div className="flex items-center gap-2.5">
              <Skeleton className="h-8 w-8 rounded-full" />
              <Skeleton className="h-8 w-24" />
            </div>
          </div>
          <div className="flex gap-3 pt-2">
            <Skeleton className="h-10 w-32 rounded-xl" />
            <Skeleton className="h-10 w-24 rounded-xl" />
          </div>
        </div>
      </div>
    </motion.article>
  );
}
