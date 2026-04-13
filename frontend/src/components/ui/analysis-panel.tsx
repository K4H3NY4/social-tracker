"use client";

import { motion } from "framer-motion";
import { Check, Lightbulb, Bot, ChevronDown, ChevronUp, AlertTriangle } from "lucide-react";
import { useState } from "react";
import type { ComplianceAnalysis } from "@/types";
import {
  FacebookIcon,
  InstagramIcon,
  TikTokIcon,
} from "@/components/icons/social-icons";

interface AnalysisPanelProps {
  platform: "facebook" | "instagram" | "tiktok";
  analysis: ComplianceAnalysis | null;
}

const platformMeta = {
  facebook: {
    name: "Facebook",
    Icon: FacebookIcon,
    color: "var(--color-facebook)",
  },
  instagram: {
    name: "Instagram",
    Icon: InstagramIcon,
    color: "var(--color-instagram)",
  },
  tiktok: {
    name: "TikTok",
    Icon: TikTokIcon,
    color: "var(--color-tiktok)",
  },
};

export function AnalysisPanel({ platform, analysis }: AnalysisPanelProps) {
  const [expanded, setExpanded] = useState(true);
  const meta = platformMeta[platform];

  if (!analysis) {
    return (
      <div className="bg-gradient-to-b from-[#1a1a1a] to-[#121212] rounded-[32px] border border-border p-6">
        <div className="flex items-center gap-3 text-text-tertiary">
          <meta.Icon className="w-5 h-5" />
          <span className="text-sm font-semibold">No analysis available</span>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-gradient-to-b from-[#1a1a1a] to-[#121212] rounded-[32px] border border-border overflow-hidden hover:border-border-hover transition-all"
    >
      {/* Header */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between p-6 hover:bg-white/[0.02] transition-colors"
      >
        <div className="flex items-center gap-3">
          <div
            className="w-9 h-9 rounded-2xl flex items-center justify-center"
            style={{ background: `${meta.color}15` }}
          >
            <meta.Icon className="w-4 h-4" />
          </div>
          <span className="text-sm font-bold">{meta.name} Analysis</span>
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-accent-lime/10">
            <Bot className="w-3 h-3 text-accent-lime" />
            <span className="text-[10px] font-bold text-accent-lime uppercase">AI</span>
          </div>
        </div>
        {expanded ? (
          <ChevronUp className="w-4 h-4 text-text-tertiary" />
        ) : (
          <ChevronDown className="w-4 h-4 text-text-tertiary" />
        )}
      </button>

      {/* Expandable Body */}
      {expanded && (
        <motion.div
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: "auto", opacity: 1 }}
          transition={{ duration: 0.3 }}
          className="px-6 pb-6"
        >
          {/* Analysis Text */}
          <div className="bg-[#0a0a0a] rounded-2xl p-4 mb-4">
            <p className="text-xs leading-relaxed text-text-secondary">
              {analysis.analysis || "No analysis available"}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Deliverables Met */}
            <div>
              <div className="flex items-center gap-2 mb-3">
                <Check className="w-3.5 h-3.5 text-success" />
                <span className="text-[10px] font-bold uppercase tracking-wider text-text-tertiary">
                  Met
                </span>
                {analysis.deliverables_met?.length > 0 && (
                  <span className="text-[10px] font-bold text-success bg-success/10 px-2 py-0.5 rounded-full">
                    {analysis.deliverables_met.length}
                  </span>
                )}
              </div>
              <ul className="space-y-1.5">
                {analysis.deliverables_met?.length ? (
                  analysis.deliverables_met.map((item, i) => (
                    <li
                      key={i}
                      className="flex items-start gap-2 bg-[#0a0a0a] rounded-xl px-3 py-2 text-[11px] text-text-secondary"
                    >
                      <Check className="w-3 h-3 text-success mt-0.5 flex-shrink-0" />
                      <span>{item}</span>
                    </li>
                  ))
                ) : (
                  <li className="text-[11px] text-text-tertiary px-3 py-2">
                    No deliverables tracked
                  </li>
                )}
              </ul>
            </div>

            {/* Deliverables Missing */}
            {analysis.deliverables_missing?.length > 0 && (
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <AlertTriangle className="w-3.5 h-3.5 text-danger" />
                  <span className="text-[10px] font-bold uppercase tracking-wider text-text-tertiary">
                    Missing
                  </span>
                  <span className="text-[10px] font-bold text-danger bg-danger/10 px-2 py-0.5 rounded-full">
                    {analysis.deliverables_missing.length}
                  </span>
                </div>
                <ul className="space-y-1.5">
                  {analysis.deliverables_missing.map((item, i) => (
                    <li
                      key={i}
                      className="flex items-start gap-2 bg-[#0a0a0a] rounded-xl px-3 py-2 text-[11px] text-text-secondary"
                    >
                      <AlertTriangle className="w-3 h-3 text-danger mt-0.5 flex-shrink-0" />
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Recommendations */}
            <div className={analysis.deliverables_missing?.length ? "md:col-span-2" : ""}>
              <div className="flex items-center gap-2 mb-3">
                <Lightbulb className="w-3.5 h-3.5 text-accent-lime" />
                <span className="text-[10px] font-bold uppercase tracking-wider text-text-tertiary">
                  Recommendations
                </span>
              </div>
              <ul className="space-y-1.5">
                {analysis.recommendations?.length ? (
                  analysis.recommendations.map((item, i) => (
                    <li
                      key={i}
                      className="flex items-start gap-2 bg-[#0a0a0a] rounded-xl px-3 py-2 text-[11px] text-text-secondary"
                    >
                      <Lightbulb className="w-3 h-3 text-accent-lime mt-0.5 flex-shrink-0" />
                      <span>{item}</span>
                    </li>
                  ))
                ) : (
                  <li className="text-[11px] text-text-tertiary px-3 py-2">
                    No recommendations
                  </li>
                )}
              </ul>
            </div>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}
