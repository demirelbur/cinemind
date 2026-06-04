'use client';

import { Film } from 'lucide-react';
import { motion } from 'framer-motion';

export default function AppHeader() {
  return (
    <motion.header
      className="mb-12 pt-8 text-center md:pt-12"
      initial={{ opacity: 0, y: -12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
    >
      <div className="flex items-center justify-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-red-600/10">
          <Film className="h-5 w-5 text-red-500" />
        </div>
        <h1 className="text-4xl font-bold tracking-tight text-white md:text-[44px]">
          Cine<span className="text-red-500">Mind</span>
        </h1>
      </div>
      <motion.p
        className="mt-2 text-[14px] text-zinc-500"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.25 }}
      >
        Grounded AI-powered movie recommendations
      </motion.p>
    </motion.header>
  );
}
