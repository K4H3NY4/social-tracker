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
    color: "#ffffff",
    accentColor: "#1877f2",
    gradient: "linear-gradient(145deg, #1565c0 0%, #0d47a1 50%, #0a3d8f 100%)",
    headerGradient: "linear-gradient(135deg, #42a5f5, #1877f2)",
    border: "rgba(66,165,245,0.25)",
    innerBg: "rgba(255,255,255,0.08)",
    aiBadgeBg: "rgba(255,255,255,0.15)",
    textPrimary: "#ffffff",
    textSecondary: "rgba(255,255,255,0.8)",
    textMuted: "rgba(255,255,255,0.5)",
  },
  instagram: {
    name: "Instagram",
    Icon: InstagramIcon,
    color: "#ffffff",
    accentColor: "#e1306c",
    gradient: "linear-gradient(145deg, #c2185b 0%, #8e24aa 50%, #6a1b9a 100%)",
    headerGradient: "linear-gradient(135deg, #f58529, #dd2a7b, #8134af)",
    border: "rgba(225,48,108,0.25)",
    innerBg: "rgba(255,255,255,0.08)",
    aiBadgeBg: "rgba(255,255,255,0.15)",
    textPrimary: "#ffffff",
    textSecondary: "rgba(255,255,255,0.8)",
    textMuted: "rgba(255,255,255,0.5)",
  },
  tiktok: {
    name: "TikTok",
    Icon: TikTokIcon,
    color: "#00f2ea",
    accentColor: "#00f2ea",
    gradient: "linear-gradient(145deg, #1a1a1a 0%, #111111 50%, #0a0a0a 100%)",
    headerGradient: "linear-gradient(135deg, #010101, #1a1a1a)",
    border: "rgba(0,242,234,0.25)",
    innerBg: "rgba(0,242,234,0.06)",
    aiBadgeBg: "rgba(0,242,234,0.15)",
    textPrimary: "#ffffff",
    textSecondary: "rgba(255,255,255,0.75)",
    textMuted: "rgba(255,255,255,0.45)",
  },
};

export function AnalysisPanel({ platform, analysis }: AnalysisPanelProps) {
  const [expanded, setExpanded] = useState(true);
  const meta = platformMeta[platform];

  if (!analysis) {
    return (
      <div
        className="rounded-[24px] sm:rounded-[32px] border p-4 sm:p-6"
        style={{ background: meta.gradient, borderColor: meta.border }}
      >
        <div className="flex items-center gap-3" style={{ color: meta.textMuted }}>
          <div
            className="w-9 h-9 rounded-2xl flex items-center justify-center"
            style={{ background: meta.headerGradient }}
          >
            <meta.Icon className="w-4 h-4 text-white" />
          </div>
          <span className="text-sm font-semibold">No analysis available</span>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-[24px] sm:rounded-[32px] border overflow-hidden transition-all"
      style={{ background: meta.gradient, borderColor: meta.border }}
    >
      {/* Header */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between p-4 sm:p-6 hover:brightness-110 transition-all"
      >
        <div className="flex items-center gap-3">
          <div
            className="w-10 h-10 rounded-2xl flex items-center justify-center shadow-lg"
            style={{ background: meta.headerGradient }}
          >
            <meta.Icon className="w-5 h-5 text-white" />
          </div>
          <span className="text-sm font-bold" style={{ color: meta.textPrimary }}>{meta.name} Analysis</span>
          <div
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-full"
            style={{ background: meta.aiBadgeBg }}
          >
            <Bot className="w-3 h-3" style={{ color: "#ffffff" }} />
            <span className="text-[10px] font-bold uppercase" style={{ color: "#ffffff" }}>AI</span>
          </div>
        </div>
        {expanded ? (
          <ChevronUp className="w-4 h-4" style={{ color: meta.textMuted }} />
        ) : (
          <ChevronDown className="w-4 h-4" style={{ color: meta.textMuted }} />
        )}
      </button>

      {/* Expandable Body */}
      {expanded && (
        <motion.div
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: "auto", opacity: 1 }}
          transition={{ duration: 0.3 }}
          className="px-4 sm:px-6 pb-4 sm:pb-6"
        >
          {/* Analysis Text */}
          <div className="rounded-2xl p-4 mb-4" style={{ background: meta.innerBg }}>
            <p className="text-xs leading-relaxed" style={{ color: meta.textSecondary }}>
              {analysis.analysis || "No analysis available"}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Deliverables Met */}
            <div>
              <div className="flex items-center gap-2 mb-3">
                <Check className="w-3.5 h-3.5 text-success" />
                <span className="text-[10px] font-bold uppercase tracking-wider" style={{ color: meta.textMuted }}>
                  Met
                </span>
                {analysis.deliverables_met?.length > 0 && (
                  <span className="text-[10px] font-bold text-success bg-success/20 px-2 py-0.5 rounded-full">
                    {analysis.deliverables_met.length}
                  </span>
                )}
              </div>
              <ul className="space-y-1.5">
                {analysis.deliverables_met?.length ? (
                  analysis.deliverables_met.map((item, i) => (
                    <li
                      key={i}
                      className="flex items-start gap-2 rounded-xl px-3 py-2 text-[11px]"
                    style={{ background: meta.innerBg, color: meta.textSecondary }}
                    >
                      <Check className="w-3 h-3 text-success mt-0.5 flex-shrink-0" />
                      <span>{item}</span>
                    </li>
                  ))
                ) : (
                  <li className="text-[11px] px-3 py-2" style={{ color: meta.textMuted }}>
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
                  <span className="text-[10px] font-bold uppercase tracking-wider" style={{ color: meta.textMuted }}>
                    Missing
                  </span>
                  <span className="text-[10px] font-bold text-danger bg-danger/20 px-2 py-0.5 rounded-full">
                    {analysis.deliverables_missing.length}
                  </span>
                </div>
                <ul className="space-y-1.5">
                  {analysis.deliverables_missing.map((item, i) => (
                    <li
                      key={i}
                      className="flex items-start gap-2 rounded-xl px-3 py-2 text-[11px]"
                    style={{ background: meta.innerBg, color: meta.textSecondary }}
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
                <Lightbulb className="w-3.5 h-3.5" style={{ color: meta.accentColor }} />
                <span className="text-[10px] font-bold uppercase tracking-wider" style={{ color: meta.textMuted }}>
                  Recommendations
                </span>
              </div>
              <ul className="space-y-1.5">
                {analysis.recommendations?.length ? (
                  analysis.recommendations.map((item, i) => (
                    <li
                      key={i}
                      className="flex items-start gap-2 rounded-xl px-3 py-2 text-[11px]"
                    style={{ background: meta.innerBg, color: meta.textSecondary }}
                    >
                      <Lightbulb className="w-3 h-3 mt-0.5 flex-shrink-0" style={{ color: meta.accentColor }} />
                      <span>{item}</span>
                    </li>
                  ))
                ) : (
                  <li className="text-[11px] px-3 py-2" style={{ color: meta.textMuted }}>
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
