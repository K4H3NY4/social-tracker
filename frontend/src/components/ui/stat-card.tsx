"use client";

import { motion } from "framer-motion";

interface StatCardProps {
  label: string;
  value: string | number;
  subtitle?: string;
  trend?: "up" | "down" | "neutral";
  trendValue?: string;
  accentColor?: string;
}

export function StatCard({
  label,
  value,
  subtitle,
  trend,
  trendValue,
  accentColor,
}: StatCardProps) {
  return (
    <div className="flex flex-col gap-1.5">
      <span className="text-[10px] font-bold uppercase tracking-widest text-text-tertiary">
        {label}
      </span>
      <div className="flex items-baseline gap-2">
        <span
          className="font-[family-name:var(--font-space-grotesk)] text-2xl font-bold"
          style={accentColor ? { color: accentColor } : {}}
        >
          {value}
        </span>
        {trend && trendValue && (
          <motion.span
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            className={`text-xs font-semibold ${
              trend === "up"
                ? "text-success"
                : trend === "down"
                  ? "text-danger"
                  : "text-text-secondary"
            }`}
          >
            {trend === "up" ? "↑" : trend === "down" ? "↓" : "→"} {trendValue}
          </motion.span>
        )}
      </div>
      {subtitle && (
        <span className="text-[11px] text-text-tertiary">{subtitle}</span>
      )}
    </div>
  );
}
