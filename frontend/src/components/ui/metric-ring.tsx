"use client";

import { motion } from "framer-motion";

interface MetricRingProps {
  score: number;
  label: string;
  color: string;
  size?: number;
  strokeWidth?: number;
}

export function MetricRing({
  score,
  label,
  color,
  size = 100,
  strokeWidth = 8,
}: MetricRingProps) {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className="flex flex-col items-center gap-3">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="-rotate-90">
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="#1a1a1a"
            strokeWidth={strokeWidth}
          />
          <motion.circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 1.2, ease: "easeOut" }}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <motion.span
            className="font-[family-name:var(--font-space-grotesk)] text-2xl font-bold"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            {score}
          </motion.span>
        </div>
      </div>
      <span className="text-[11px] font-semibold uppercase tracking-wider text-text-secondary">
        {label}
      </span>
    </div>
  );
}
