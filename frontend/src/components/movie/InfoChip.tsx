'use client';

import { cn } from '@/lib/utils';

interface InfoChipProps {
  label: string;
  variant?: 'default' | 'accent' | 'success';
}

export default function InfoChip({
  label,
  variant = 'default',
}: InfoChipProps) {
  return (
    <span
      className={cn(
        'inline-flex h-7 items-center rounded-full px-3 text-xs font-medium',
        variant === 'default' &&
          'bg-white/5 text-zinc-300 border border-white/10',
        variant === 'accent' &&
          'bg-red-500/8 text-red-400 border border-red-500/20',
        variant === 'success' &&
          'bg-[rgba(34,197,94,0.08)] text-green-400 border border-[rgba(34,197,94,0.2)]',
      )}
    >
      {label}
    </span>
  );
}
