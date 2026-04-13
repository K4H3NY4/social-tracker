"use client";

import { motion } from "framer-motion";
import { TrendingUp, TrendingDown, Minus, Sparkles, ArrowUpRight, Clock, Target } from "lucide-react";
import { cn } from "@/lib/utils";
import type { MarketingInsight } from "@/lib/mock-data";

const impactColors = {
  high: { bg: "bg-accent/10", text: "text-accent", badge: "High Impact" },
  medium: { bg: "bg-neon-blue/10", text: "text-neon-blue", badge: "Medium" },
  low: { bg: "bg-text-muted/10", text: "text-text-muted", badge: "Low" },
};

const trendIcons = {
  up: TrendingUp,
  down: TrendingDown,
  neutral: Minus,
};

interface GrowthInsightsPanelProps {
  insights: MarketingInsight[];
  platform: string;
  platformColor: string;
}

export function GrowthInsightsPanel({
  insights,
  platform,
  platformColor,
}: GrowthInsightsPanelProps) {
  return (
    <div className="bg-bg-card rounded-xl border border-border overflow-hidden">
      <div className="p-5 pb-3 flex items-center gap-2">
        <Sparkles className="w-4 h-4" style={{ color: platformColor }} />
        <h3 className="text-sm font-bold uppercase tracking-wider text-text-secondary">
          Growth Insights
        </h3>
      </div>
      <div className="px-5 pb-5 space-y-3">
        {insights.map((insight, i) => {
          const impact = impactColors[insight.impact];
          const TrendIcon = insight.trend ? trendIcons[insight.trend] : Minus;
          return (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: -12 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.08, duration: 0.3 }}
              className="bg-bg-elevated rounded-lg p-4 border border-transparent hover:border-border-hover transition-all duration-200"
            >
              <div className="flex items-start justify-between gap-3 mb-1.5">
                <div className="flex items-center gap-2">
                  <h4 className="text-sm font-semibold text-text-primary">
                    {insight.title}
                  </h4>
                  <span
                    className={cn(
                      "text-[9px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded",
                      impact.bg,
                      impact.text
                    )}
                  >
                    {impact.badge}
                  </span>
                </div>
                {insight.metric && (
                  <span
                    className={cn(
                      "flex items-center gap-1 text-xs font-mono font-bold shrink-0",
                      insight.trend === "up" && "text-success",
                      insight.trend === "down" && "text-danger",
                      insight.trend === "neutral" && "text-text-muted"
                    )}
                  >
                    <TrendIcon className="w-3 h-3" />
                    {insight.metric}
                  </span>
                )}
              </div>
              <p className="text-xs text-text-secondary leading-relaxed">
                {insight.description}
              </p>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}

interface QuickInsightProps {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  value: string;
  sublabel?: string;
  color?: string;
}

export function QuickInsight({ icon: Icon, label, value, sublabel, color }: QuickInsightProps) {
  return (
    <div className="bg-bg-elevated rounded-lg p-3 flex items-center gap-3">
      <div
        className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0"
        style={{ backgroundColor: color ? `color-mix(in srgb, ${color} 12%, transparent)` : undefined }}
      >
        <Icon className="w-4 h-4" />
      </div>
      <div className="min-w-0">
        <p className="text-xs text-text-muted">{label}</p>
        <p className="text-sm font-bold font-mono" style={{ color }}>
          {value}
        </p>
        {sublabel && <p className="text-[10px] text-text-muted">{sublabel}</p>}
      </div>
    </div>
  );
}
