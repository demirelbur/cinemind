'use client';

import { motion } from 'framer-motion';

import { Skeleton } from '@/components/ui/skeleton';

export default function MovieCardSkeleton({ index = 0 }: { index?: number }) {
  return (
    <motion.article
      className="overflow-hidden rounded-2xl border border-white/[0.06]"
      style={{ background: 'linear-gradient(145deg, rgba(255,255,255,0.025), rgba(255,255,255,0.005))' }}
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.08 }}
    >
      <div className="p-5">
        <div className="flex items-start justify-between gap-4">
          <div className="space-y-1.5">
            <Skeleton className="h-6 w-52" />
            <Skeleton className="h-3 w-40" />
            <Skeleton className="h-3 w-28" />
          </div>
          <Skeleton className="h-10 w-20" />
        </div>
        <div className="mt-2 flex gap-1.5">
          <Skeleton className="h-5 w-16 rounded-full" />
          <Skeleton className="h-5 w-16 rounded-full" />
          <Skeleton className="h-5 w-20 rounded-full" />
        </div>
        <div className="mt-3 space-y-1">
          <Skeleton className="h-3 w-full" />
          <Skeleton className="h-3 w-2/3" />
        </div>
        <div className="mt-3 flex gap-4">
          <Skeleton className="h-3 w-24" />
          <Skeleton className="h-3 w-28" />
        </div>
        <div className="mt-2 flex gap-2">
          <Skeleton className="h-9 w-20 rounded-lg" />
          <Skeleton className="h-9 w-20 rounded-lg" />
        </div>
      </div>
    </motion.article>
  );
}
