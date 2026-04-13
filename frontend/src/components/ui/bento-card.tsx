"use client";

import { motion } from "framer-motion";
import type { ReactNode } from "react";

interface BentoCardProps {
  children: ReactNode;
  className?: string;
  delay?: number;
  gradient?: string;
}

export function BentoCard({
  children,
  className = "",
  delay = 0,
  gradient,
}: BentoCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay, ease: "easeOut" }}
      className={`${
        gradient || "bg-gradient-to-b from-[#1a1a1a] to-[#121212]"
      } rounded-[32px] border border-border transition-all hover:border-border-hover hover:-translate-y-0.5 ${className}`}
    >
      {children}
    </motion.div>
  );
}
