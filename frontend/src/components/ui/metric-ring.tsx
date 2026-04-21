"use client";

import { motion } from "framer-motion";
import { getHeatColor } from "@/lib/utils";
import type { ReactNode } from "react";

interface MetricRingProps {
  score: number;
  label: string;
  icon?: ReactNode;
  color: string;
  size?: number;
  strokeWidth?: number;
}

export function MetricRing({
  score,
  label,
  icon,
  color,
  size = 100,
  strokeWidth = 8,
}: MetricRingProps) {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const clampedScore = Math.min(score, 100);
  const offset = circumference - (clampedScore / 100) * circumference;
  const heatColor = getHeatColor(score);
  const isOver100 = score > 100;

  return (
    <div className="flex flex-col items-center gap-2">
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
            stroke={heatColor}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 1.2, ease: "easeOut" }}
          />
          {/* Glow ring for overachievement */}
          {isOver100 && (
            <motion.circle
              cx={size / 2}
              cy={size / 2}
              r={radius}
              fill="none"
              stroke={heatColor}
              strokeWidth={strokeWidth + 2}
              strokeLinecap="round"
              strokeDasharray={circumference}
              initial={{ strokeDashoffset: circumference, opacity: 0 }}
              animate={{ strokeDashoffset: 0, opacity: 0.25 }}
              transition={{ duration: 1.5, ease: "easeOut" }}
              style={{ filter: "blur(3px)" }}
            />
          )}
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <motion.span
            className={`font-[family-name:var(--font-space-grotesk)] font-bold ${score >= 1000 ? "text-sm" : score >= 100 ? "text-lg" : "text-2xl"}`}
            style={{ color: heatColor }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            {score}%
          </motion.span>
        </div>
      </div>
      {icon ? (
        <div className="flex flex-col items-center gap-0.5">
          <div style={{ color }}>{icon}</div>
          <span className="text-[9px] font-semibold uppercase tracking-wider text-text-tertiary">
            {label}
          </span>
        </div>
      ) : (
        <span className="text-[11px] font-semibold uppercase tracking-wider text-text-secondary">
          {label}
        </span>
      )}
    </div>
  );
}
