"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { RefreshCw, BarChart3, Target, Users, Zap, Film, Image as ImageIcon, Layers, Handshake, ExternalLink, ChevronDown, Calendar, TrendingUp, TrendingDown } from "lucide-react";
import { motion } from "framer-motion";

import { BentoCard } from "@/components/ui/bento-card";
import { MetricRing } from "@/components/ui/metric-ring";
import { AnalysisPanel } from "@/components/ui/analysis-panel";
import { LoadingState, EmptyState } from "@/components/ui/loading-states";
import {
  FacebookIcon,
  InstagramIcon,
  TikTokIcon,
} from "@/components/icons/social-icons";

import {
  getClients,
  getFacebookCompliance,
  getInstagramCompliance,
  getTikTokCompliance,
  clearCache,
} from "@/lib/api";
import { getComplianceStatus, getDefaultDateRange, getHeatColor, getHeatTextClass, getHeatBgClass, getHeatCardStyle } from "@/lib/utils";
import { parseContractTargets } from "@/lib/contract-targets";

import type {
  Client,
  FacebookComplianceData,
  InstagramComplianceData,
  TikTokComplianceData,
} from "@/types";

/* Progress Bar */
function ProgressBar({ value, max, color, label }: { value: number; max: number; color: string; label: string }) {
  const pct = max > 0 ? Math.round((value / max) * 100) : 0;
  return (
    <div className="flex items-center gap-3">
      <span className="text-xs text-text-tertiary w-16 truncate font-medium">{label}</span>
      <div className="flex-1 h-2.5 rounded-full bg-[#0a0a0a] overflow-hidden">
        <motion.div
          className="h-full rounded-full"
          style={{ background: color }}
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.8, ease: "easeOut" }}
        />
      </div>
      <span className="font-[family-name:var(--font-space-grotesk)] text-sm font-bold w-10 text-right">{value}</span>
    </div>
  );
}

/* Main Dashboard */
export function DashboardClient() {
  const [clients, setClients] = useState<Client[]>([]);
  const [selectedClient, setSelectedClient] = useState<Client | null>(null);
  const [dateRange, setDateRange] = useState(getDefaultDateRange);

  const [fbData, setFbData] = useState<FacebookComplianceData | null>(null);
  const [igData, setIgData] = useState<InstagramComplianceData | null>(null);
  const [ttData, setTtData] = useState<TikTokComplianceData | null>(null);

  const [loading, setLoading] = useState(false);
  const [hasData, setHasData] = useState(false);
  const [loadingPlatform, setLoadingPlatform] = useState<string | null>(null);

  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    getClients()
      .then((res) => {
        setClients(res.clients);
        if (res.clients.length > 0) {
          setSelectedClient(res.clients[0]);
        }
      })
      .catch(console.error);
  }, []);

  // Load data SEQUENTIALLY to avoid overwhelming the backend
  // clearData=true when switching clients (wipe old data), false when refreshing dates (keep showing stale)
  const loadData = useCallback(async (clearData = true) => {
    if (!selectedClient) return;

    if (abortRef.current) abortRef.current.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setLoading(true);
    if (clearData) {
      setHasData(false);
      setFbData(null);
      setIgData(null);
      setTtData(null);
    }

    try {
      if (selectedClient.facebook && !controller.signal.aborted) {
        setLoadingPlatform("Facebook");
        try {
          const fb = await getFacebookCompliance(selectedClient.facebook, dateRange.start, dateRange.end);
          if (!controller.signal.aborted) { setFbData(fb); setHasData(true); }
        } catch (e) { console.error("FB error:", e); }
      }

      if (selectedClient.instagram && !controller.signal.aborted) {
        setLoadingPlatform("Instagram");
        try {
          const ig = await getInstagramCompliance(selectedClient.instagram, dateRange.start, dateRange.end);
          if (!controller.signal.aborted) { setIgData(ig); setHasData(true); }
        } catch (e) { console.error("IG error:", e); }
      }

      if (selectedClient.tiktok && !controller.signal.aborted) {
        setLoadingPlatform("TikTok");
        try {
          const tt = await getTikTokCompliance(selectedClient.tiktok, dateRange.start, dateRange.end);
          if (!controller.signal.aborted) { setTtData(tt); setHasData(true); }
        } catch (e) { console.error("TT error:", e); }
      }
    } catch (err) {
      console.error(err);
    } finally {
      if (!controller.signal.aborted) {
        setLoading(false);
        setLoadingPlatform(null);
      }
    }
  }, [selectedClient, dateRange]);

  // Auto-load when client changes
  const prevClientIdRef = useRef<number | null>(null);
  useEffect(() => {
    if (selectedClient && selectedClient.id !== prevClientIdRef.current) {
      prevClientIdRef.current = selectedClient.id;
      loadData(true);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedClient?.id]);

  const fbScore = fbData?.compliance_analysis?.compliance_score ?? 0;
  const igScore = igData?.compliance_analysis?.compliance_score ?? 0;
  const ttScore = ttData?.compliance_analysis?.compliance_score ?? 0;
  const activePlatforms = [fbData, igData, ttData].filter(Boolean).length;
  const avgScore = activePlatforms > 0 ? Math.round((fbScore + igScore + ttScore) / activePlatforms) : 0;

  const fbPosts = fbData?.total_posts_delivered ?? 0;
  const igPosts = igData?.total_posts_delivered ?? 0;
  const ttPosts = ttData?.total_videos_delivered ?? 0;
  const totalPosts = fbPosts + igPosts + ttPosts;

  // Extract first number from a freeform string (e.g. "12 posts per month" → 12)
  const extractNum = (s?: string) => { const m = s?.match(/(\d+)/); return m ? parseInt(m[1], 10) : 0; };

  // Contract targets — use parsed contract as primary source, AI post_frequency as fallback
  const contractTargets = parseContractTargets(selectedClient?.contract ?? undefined);
  const fbRequired = contractTargets.facebook || extractNum(fbData?.compliance_analysis?.post_frequency?.required);
  const igRequired = contractTargets.instagram || extractNum(igData?.compliance_analysis?.post_frequency?.required);
  const ttRequired = contractTargets.tiktok || extractNum(ttData?.compliance_analysis?.post_frequency?.required);
  const totalRequired = fbRequired + igRequired + ttRequired;

  return (
    <div className="min-h-screen pb-24 lg:pb-6">
      {/* Controls Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 sm:gap-3 px-4 sm:px-5 py-3 sm:py-4 sticky top-[56px] sm:top-[72px] z-30 bg-bg-primary/60 backdrop-blur-2xl border-b border-white/[0.04]">
        {/* Client Select */}
        <div className="relative flex-[2] min-w-0 group">
          <div className="absolute left-4 top-1/2 -translate-y-1/2 pointer-events-none">
            <Users className="w-4 h-4 text-text-tertiary group-focus-within:text-accent-lime transition-colors" />
          </div>
          <select
            className="w-full bg-[#1a1a1a] border border-white/[0.08] text-text-primary rounded-2xl pl-10 pr-10 py-3 text-sm font-semibold outline-none focus:border-accent-lime/40 focus:bg-[#222] transition-all appearance-none cursor-pointer [&>option]:bg-[#1a1a1a] [&>option]:text-white [&>option]:py-2"
            value={selectedClient?.id ?? ""}
            onChange={(e) => {
              const client = clients.find((c) => c.id === Number(e.target.value));
              if (client) setSelectedClient(client);
            }}
          >
            <option value="">Select a client...</option>
            {clients.map((c) => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
          <ChevronDown className="absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 text-text-tertiary pointer-events-none" />
        </div>

        {/* Date Range */}
        <div className="flex gap-2 flex-1">
          <div className="relative flex-1 group">
            <div className="absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none">
              <Calendar className="w-3.5 h-3.5 text-text-tertiary group-focus-within:text-accent-lime transition-colors" />
            </div>
            <input
              type="date"
              className="w-full bg-white/[0.04] border border-white/[0.06] text-text-primary rounded-2xl pl-9 pr-3 py-3 text-sm font-semibold outline-none focus:border-accent-lime/40 focus:bg-white/[0.06] transition-all"
              value={dateRange.start}
              onChange={(e) => setDateRange((prev) => ({ ...prev, start: e.target.value }))}
            />
          </div>
          <span className="self-center text-text-tertiary text-xs font-bold">to</span>
          <div className="relative flex-1 group">
            <div className="absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none">
              <Calendar className="w-3.5 h-3.5 text-text-tertiary group-focus-within:text-accent-lime transition-colors" />
            </div>
            <input
              type="date"
              className="w-full bg-white/[0.04] border border-white/[0.06] text-text-primary rounded-2xl pl-9 pr-3 py-3 text-sm font-semibold outline-none focus:border-accent-lime/40 focus:bg-white/[0.06] transition-all"
              value={dateRange.end}
              onChange={(e) => setDateRange((prev) => ({ ...prev, end: e.target.value }))}
            />
          </div>
        </div>

        <button
          onClick={() => { clearCache(); loadData(false); }}
          disabled={loading || !selectedClient}
          className="flex items-center justify-center gap-2 bg-accent-lime text-bg-primary px-6 py-3 rounded-2xl font-bold text-sm uppercase tracking-wide hover:brightness-110 active:scale-[0.98] disabled:opacity-40 disabled:cursor-not-allowed transition-all shadow-[0_0_20px_rgba(204,243,129,0.15)]"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          <span className="hidden sm:inline">Refresh</span>
        </button>
      </div>

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center py-20">
          <div className="flex flex-col items-center gap-4">
            <div className="w-12 h-12 rounded-full border-2 border-border flex items-center justify-center">
              <RefreshCw className="w-6 h-6 text-accent-lime animate-spin" />
            </div>
            <span className="text-sm text-text-tertiary font-medium">
              {loadingPlatform ? `Loading ${loadingPlatform}...` : "Analyzing compliance..."}
            </span>
            {(fbData || igData) && (
              <span className="text-xs text-text-tertiary">
                {[fbData && "Facebook done", igData && "Instagram done"].filter(Boolean).join(" \u00b7 ")}
              </span>
            )}
          </div>
        </div>
      )}
      {!loading && !hasData && <EmptyState />}

      {/* Main Bento Grid — render even while loading so partial data shows */}
      {hasData && (
        <div className="px-4 sm:px-5 py-4 sm:py-6 space-y-4 sm:space-y-5 max-w-[1400px] mx-auto">

          {/* Inline loading banner for subsequent platform loads */}
          {loading && loadingPlatform && (
            <div className="flex items-center gap-3 bg-accent-lime/10 border border-accent-lime/20 rounded-2xl px-5 py-3">
              <RefreshCw className="w-4 h-4 text-accent-lime animate-spin flex-shrink-0" />
              <span className="text-sm font-semibold text-accent-lime">Loading {loadingPlatform}...</span>
              <span className="text-xs text-text-tertiary ml-auto">
                {[fbData && "Facebook ✓", igData && "Instagram ✓", ttData && "TikTok ✓"].filter(Boolean).join("  ·  ")}
              </span>
            </div>
          )}

          {/* ROW 1: Hero + Score Rings + Stacked */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 sm:gap-5">

            {/* HERO CARD — dynamic heat-map bg */}
            {(() => {
              const heroStyle = getHeatCardStyle(avgScore);
              return (
                <motion.div
                  initial={{ opacity: 0, y: 16 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4, ease: "easeOut" }}
                  style={{ background: heroStyle.background }}
                  className="lg:col-span-4 p-5 sm:p-7 relative overflow-hidden min-h-[280px] sm:min-h-[340px] flex flex-col justify-between rounded-[24px] sm:rounded-[32px] border border-white/10 transition-all hover:border-white/20 hover:-translate-y-0.5"
                >
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <Zap className="w-5 h-5" style={{ color: heroStyle.text }} />
                      <span className="text-[11px] font-bold uppercase tracking-widest" style={{ color: heroStyle.textMuted }}>
                        Compliance Score
                      </span>
                    </div>
                    <div className="font-[family-name:var(--font-space-grotesk)] text-[64px] sm:text-[80px] lg:text-[112px] font-bold leading-[0.85] tracking-tighter" style={{ color: heroStyle.text }}>
                      {avgScore}%
                    </div>
                    <div className="mt-3 text-lg sm:text-xl font-bold" style={{ color: heroStyle.textMuted }}>
                      {getComplianceStatus(avgScore)}
                    </div>

                    {/* Mini sparkline — platform score trend */}
                    {(() => {
                      const platforms: { name: string; score: number }[] = [];
                      if (fbData) platforms.push({ name: "FB", score: fbScore });
                      if (igData) platforms.push({ name: "IG", score: igScore });
                      if (ttData) platforms.push({ name: "TT", score: ttScore });
                      if (platforms.length < 2) return null;

                      const scores = platforms.map((p) => p.score);
                      const min = Math.min(...scores, 0);
                      const max = Math.max(...scores, 100);
                      const range = max - min || 1;
                      const w = 120;
                      const h = 36;
                      const pad = 4;

                      const pts = scores.map((s, i) => ({
                        x: pad + (i / (scores.length - 1)) * (w - pad * 2),
                        y: h - pad - ((s - min) / range) * (h - pad * 2),
                      }));
                      const polyline = pts.map((p) => `${p.x},${p.y}`).join(" ");
                      const trending = scores[scores.length - 1] >= scores[0];

                      return (
                        <div className="mt-3 flex items-center gap-2">
                          <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} className="overflow-visible">
                            <defs>
                              <linearGradient id="sparkGrad" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="0%" stopColor={heroStyle.text} stopOpacity={0.3} />
                                <stop offset="100%" stopColor={heroStyle.text} stopOpacity={0} />
                              </linearGradient>
                            </defs>
                            <polygon
                              points={`${pts[0].x},${h - pad} ${polyline} ${pts[pts.length - 1].x},${h - pad}`}
                              fill="url(#sparkGrad)"
                            />
                            <polyline
                              points={polyline}
                              fill="none"
                              stroke={heroStyle.text}
                              strokeWidth={2}
                              strokeLinecap="round"
                              strokeLinejoin="round"
                            />
                            {pts.map((pt, i) => (
                              <circle key={i} cx={pt.x} cy={pt.y} r={3} fill={heroStyle.text} stroke="#000" strokeWidth={1.5} />
                            ))}
                          </svg>
                          <div className="flex items-center gap-1" style={{ color: heroStyle.textMuted }}>
                            {trending ? <TrendingUp className="w-3.5 h-3.5" /> : <TrendingDown className="w-3.5 h-3.5" />}
                            <span className="text-[10px] font-bold uppercase tracking-wide">
                              {platforms.map((p) => p.name).join(" → ")}
                            </span>
                          </div>
                        </div>
                      );
                    })()}
                  </div>
                  <div className="mt-4 backdrop-blur-sm rounded-2xl p-4" style={{ background: heroStyle.overlay }}>
                    <p className="text-sm font-semibold" style={{ color: heroStyle.textMuted }}>
                      {activePlatforms} active platform{activePlatforms !== 1 ? "s" : ""} &bull; {totalPosts} deliverables tracked
                    </p>
                  </div>
                </motion.div>
              );
            })()}

            {/* PLATFORM SCORE RINGS — deliverable % */}
            <BentoCard className="lg:col-span-5 p-5 sm:p-7" delay={0.05}>
              <div className="flex items-center justify-between mb-6 sm:mb-8">
                <div className="flex items-center gap-2">
                  <Target className="w-4 h-4 text-accent-purple" />
                  <span className="text-xs font-bold uppercase tracking-widest text-text-tertiary">
                    Platform Scores
                  </span>
                </div>
                <span className="text-[10px] font-bold text-accent-lime bg-accent-lime/10 px-3 py-1 rounded-full uppercase">
                  Live
                </span>
              </div>
              {(() => {
                const fbDelPct = fbRequired > 0 ? Math.round((fbPosts / fbRequired) * 100) : 0;
                const igDelPct = igRequired > 0 ? Math.round((igPosts / igRequired) * 100) : 0;
                const ttDelPct = ttRequired > 0 ? Math.round((ttPosts / ttRequired) * 100) : 0;
                return (
                  <div className="flex items-center justify-around flex-wrap gap-4">
                    <MetricRing score={fbDelPct} icon={<FacebookIcon className="w-4 h-4 sm:w-5 sm:h-5" />} color="var(--color-facebook)" size={100} />
                    <MetricRing score={igDelPct} icon={<InstagramIcon className="w-4 h-4 sm:w-5 sm:h-5" />} color="var(--color-instagram)" size={100} />
                    <MetricRing score={ttDelPct} icon={<TikTokIcon className="w-4 h-4 sm:w-5 sm:h-5" />} color="var(--color-tiktok)" size={100} />
                  </div>
                );
              })()}

              {/* Deliverables summary */}
              <div className="grid grid-cols-3 gap-2 mt-6 pt-5 border-t border-white/[0.06]">
                {[
                  { label: "FB", delivered: fbPosts, required: fbRequired, color: "var(--color-facebook)" },
                  { label: "IG", delivered: igPosts, required: igRequired, color: "var(--color-instagram)" },
                  { label: "TT", delivered: ttPosts, required: ttRequired, color: "var(--color-tiktok)" },
                ].map((p) => {
                  const delPct = p.required > 0 ? Math.round((p.delivered / p.required) * 100) : 0;
                  return (
                    <div key={p.label} className="text-center">
                      <div className="text-[10px] text-text-tertiary font-bold mb-1">{p.label} Deliverables</div>
                      <div className={`font-[family-name:var(--font-space-grotesk)] text-lg font-bold ${getHeatTextClass(delPct)}`}>
                        {p.delivered}<span className="text-text-tertiary font-normal text-xs">/{p.required || "—"}</span>
                      </div>
                      <div className="h-1.5 bg-[#0a0a0a] rounded-full overflow-hidden mt-1.5 mx-2">
                        <motion.div className="h-full rounded-full" style={{ background: p.color }} initial={{ width: 0 }} animate={{ width: `${Math.min(delPct, 100)}%` }} transition={{ duration: 0.8 }} />
                      </div>
                    </div>
                  );
                })}
              </div>
            </BentoCard>

            {/* RIGHT stacked */}
            <div className="lg:col-span-3 grid grid-cols-2 lg:grid-cols-1 lg:grid-rows-2 gap-5">
              <BentoCard
                delay={0.1}
                gradient="bg-gradient-to-br from-[#7928ca] to-[#4c1d95]"
                className="p-5 sm:p-6 flex flex-col justify-between min-h-[140px] sm:min-h-[160px]"
              >
                <span className="text-[10px] font-bold uppercase tracking-widest text-white/50">
                  Total Deliverables
                </span>
                <div>
                  <div className="font-[family-name:var(--font-space-grotesk)] text-4xl sm:text-6xl font-bold text-white leading-none">
                    {totalPosts}
                  </div>
                  <span className="text-xs sm:text-sm text-white/50 font-medium">pieces delivered</span>
                </div>
              </BentoCard>

              <BentoCard delay={0.15} className="p-5 flex flex-col justify-between">
                <div className="flex items-center gap-2 mb-3">
                  <BarChart3 className="w-4 h-4 text-accent-blue" />
                  <span className="text-[10px] font-bold uppercase tracking-widest text-text-tertiary">
                    Content Split
                  </span>
                </div>
                <div className="space-y-2.5">
                  <ProgressBar value={fbPosts} max={totalPosts || 1} color="var(--color-facebook)" label="FB" />
                  <ProgressBar value={igPosts} max={totalPosts || 1} color="var(--color-instagram)" label="IG" />
                  <ProgressBar value={ttPosts} max={totalPosts || 1} color="var(--color-tiktok)" label="TT" />
                </div>
              </BentoCard>
            </div>
          </div>

          {/* ROW 2: Unified Platform Cards — collapsed from previous rows 2 & 4 */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Users className="w-4 h-4 text-text-tertiary" />
              <h2 className="font-[family-name:var(--font-space-grotesk)] text-xl font-bold tracking-tight">
                Platform Overview
              </h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5">
              {/* Facebook */}
              {fbData && (() => {
                const required = fbRequired;
                const delivered = fbPosts;
                const pct = required > 0 ? Math.round((delivered / required) * 100) : 0;
                return (
                  <BentoCard delay={0.05} gradient="bg-gradient-to-br from-[#1877f2]/15 to-[#121212]" className="p-6">
                    <div className="flex items-center justify-between mb-5">
                      <div className="flex items-center gap-3">
                        <div className="w-11 h-11 rounded-2xl bg-facebook/20 flex items-center justify-center text-facebook">
                          <FacebookIcon className="w-5 h-5" />
                        </div>
                        <div>
                          <div className="font-semibold text-base">Facebook</div>
                          {selectedClient?.facebook && (
                            <div className="text-[11px] text-text-tertiary">@{selectedClient.facebook}</div>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`text-xs font-bold px-2.5 py-1 rounded-full ${getHeatBgClass(fbScore)}`}>
                          AI Compliance score is at {fbScore}%
                        </span>
                        {selectedClient?.facebook && (
                          <a href={`https://facebook.com/${selectedClient.facebook}`} target="_blank" rel="noopener noreferrer" className="w-8 h-8 rounded-full flex items-center justify-center text-text-tertiary hover:text-facebook hover:bg-facebook/10 transition-all" title="Open Facebook">
                            <ExternalLink className="w-4 h-4" />
                          </a>
                        )}
                      </div>
                    </div>

                    {/* Delivery progress */}
                    <div className="bg-[#0a0a0a] rounded-2xl p-4 mb-3">
                      <div className="flex justify-between items-baseline mb-2">
                        <span className="text-xs text-text-tertiary font-medium">Deliverables</span>
                        <span className={`font-[family-name:var(--font-space-grotesk)] text-lg font-bold ${getHeatTextClass(pct)}`}>
                          {pct > 0 ? `${pct}%` : "—"}
                        </span>
                      </div>
                      <div className="h-2 bg-[#141414] rounded-full overflow-hidden mb-2">
                        <motion.div className="h-full rounded-full" style={{ background: getHeatColor(pct) }} initial={{ width: 0 }} animate={{ width: `${Math.min(pct, 100)}%` }} transition={{ duration: 0.8, delay: 0.2 }} />
                      </div>
                      <div className="flex justify-between text-[11px]">
                        <span className="text-text-tertiary">{delivered} delivered</span>
                        <span className="text-text-tertiary">{required > 0 ? `${required} required` : "No target"}</span>
                      </div>
                      {pct > 100 && (
                        <div className="mt-2 text-[10px] font-bold text-accent-blue bg-accent-blue/10 px-2 py-0.5 rounded-full inline-block">
                          ⚡ Overachieved by {pct - 100}%
                        </div>
                      )}
                    </div>

                    {/* Content breakdown */}
                    <div className="grid grid-cols-2 gap-2 text-[11px]">
                      <div className="bg-[#0a0a0a] rounded-xl px-3 py-2.5">
                        <div className="text-text-tertiary">Static Posts</div>
                        <div className="font-[family-name:var(--font-space-grotesk)] text-lg font-bold mt-0.5">{fbData.content_breakdown?.posts ?? 0}</div>
                      </div>
                      <div className="bg-[#0a0a0a] rounded-xl px-3 py-2.5">
                        <div className="text-text-tertiary">Videos/Reels</div>
                        <div className="font-[family-name:var(--font-space-grotesk)] text-lg font-bold mt-0.5">{fbData.content_breakdown?.videos ?? 0}</div>
                      </div>
                    </div>

                    {/* Frequency Status */}
                    {fbData.compliance_analysis?.post_frequency && (
                      <div className="bg-[#0a0a0a] rounded-xl px-3 py-2.5 mt-2 text-[11px]">
                        <div className="text-text-tertiary font-bold mb-1.5">Frequency</div>
                        <div className={`font-bold ${fbData.compliance_analysis.post_frequency.status === "met" ? "text-success" : "text-warning"}`}>
                          {fbData.compliance_analysis.post_frequency.delivered} <span className="text-text-tertiary font-normal">/ {fbData.compliance_analysis.post_frequency.required} req.</span>
                        </div>
                      </div>
                    )}

                    {/* Met / Missing chips */}
                    {(fbData.compliance_analysis?.deliverables_met?.length || fbData.compliance_analysis?.deliverables_missing?.length) ? (
                      <div className="flex flex-wrap gap-1.5 mt-3">
                        {fbData.compliance_analysis.deliverables_met?.slice(0, 2).map((d, i) => (
                          <span key={i} className="text-[10px] font-semibold bg-success/10 text-success px-2 py-0.5 rounded-full">✓ {d}</span>
                        ))}
                        {fbData.compliance_analysis.deliverables_missing?.slice(0, 2).map((d, i) => (
                          <span key={i} className="text-[10px] font-semibold bg-danger/10 text-danger px-2 py-0.5 rounded-full">✗ {d}</span>
                        ))}
                      </div>
                    ) : null}
                  </BentoCard>
                );
              })()}

              {/* Instagram */}
              {igData && (() => {
                const required = igRequired;
                const delivered = igPosts;
                const pct = required > 0 ? Math.round((delivered / required) * 100) : 0;
                return (
                  <BentoCard delay={0.1} gradient="bg-gradient-to-br from-[#e1306c]/15 to-[#121212]" className="p-6">
                    <div className="flex items-center justify-between mb-5">
                      <div className="flex items-center gap-3">
                        <div className="w-11 h-11 rounded-2xl bg-instagram/20 flex items-center justify-center text-instagram">
                          <InstagramIcon className="w-5 h-5" />
                        </div>
                        <div>
                          <div className="font-semibold text-base">Instagram</div>
                          {selectedClient?.instagram && (
                            <div className="text-[11px] text-text-tertiary">@{selectedClient.instagram}</div>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`text-xs font-bold px-2.5 py-1 rounded-full ${getHeatBgClass(igScore)}`}>
                          AI Compliance score is at {igScore}%
                        </span>
                        {selectedClient?.instagram && (
                          <a href={`https://instagram.com/${selectedClient.instagram}`} target="_blank" rel="noopener noreferrer" className="w-8 h-8 rounded-full flex items-center justify-center text-text-tertiary hover:text-instagram hover:bg-instagram/10 transition-all" title="Open Instagram">
                            <ExternalLink className="w-4 h-4" />
                          </a>
                        )}
                      </div>
                    </div>

                    {/* Delivery progress */}
                    <div className="bg-[#0a0a0a] rounded-2xl p-4 mb-3">
                      <div className="flex justify-between items-baseline mb-2">
                        <span className="text-xs text-text-tertiary font-medium">Deliverables</span>
                        <span className={`font-[family-name:var(--font-space-grotesk)] text-lg font-bold ${getHeatTextClass(pct)}`}>
                          {pct > 0 ? `${pct}%` : "—"}
                        </span>
                      </div>
                      <div className="h-2 bg-[#141414] rounded-full overflow-hidden mb-2">
                        <motion.div className="h-full rounded-full" style={{ background: getHeatColor(pct) }} initial={{ width: 0 }} animate={{ width: `${Math.min(pct, 100)}%` }} transition={{ duration: 0.8, delay: 0.2 }} />
                      </div>
                      <div className="flex justify-between text-[11px]">
                        <span className="text-text-tertiary">{delivered} delivered</span>
                        <span className="text-text-tertiary">{required > 0 ? `${required} required` : "No target"}</span>
                      </div>
                      {pct > 100 && (
                        <div className="mt-2 text-[10px] font-bold text-accent-blue bg-accent-blue/10 px-2 py-0.5 rounded-full inline-block">
                          ⚡ Overachieved by {pct - 100}%
                        </div>
                      )}
                    </div>

                    {/* Content breakdown */}
                    <div className="grid grid-cols-3 gap-2 text-[11px] mb-3">
                      <div className="bg-[#0a0a0a] rounded-xl px-3 py-2.5 text-center">
                        <div className="text-text-tertiary"><Layers className="w-3 h-3 mx-auto mb-0.5" /></div>
                        <div className="font-[family-name:var(--font-space-grotesk)] text-lg font-bold">{igData.content_types?.carousel ?? 0}</div>
                        <div className="text-text-tertiary">Carousel</div>
                      </div>
                      <div className="bg-[#0a0a0a] rounded-xl px-3 py-2.5 text-center">
                        <div className="text-text-tertiary"><ImageIcon className="w-3 h-3 mx-auto mb-0.5" /></div>
                        <div className="font-[family-name:var(--font-space-grotesk)] text-lg font-bold">{igData.content_types?.image ?? 0}</div>
                        <div className="text-text-tertiary">Images</div>
                      </div>
                      <div className="bg-[#0a0a0a] rounded-xl px-3 py-2.5 text-center">
                        <div className="text-text-tertiary"><Film className="w-3 h-3 mx-auto mb-0.5" /></div>
                        <div className="font-[family-name:var(--font-space-grotesk)] text-lg font-bold">{igData.content_types?.video ?? 0}</div>
                        <div className="text-text-tertiary">Videos</div>
                      </div>
                    </div>

                    {/* Collaborations */}
                    <div className="bg-[#0a0a0a] rounded-2xl p-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Handshake className="w-3.5 h-3.5 text-accent-purple" />
                          <span className="text-[11px] font-bold text-text-tertiary">Collabs</span>
                        </div>
                        <div className="flex items-center gap-3 text-[11px]">
                          <span><span className="font-bold text-accent-purple">{igData.collaboration_stats?.collaborative_posts ?? 0}</span> collab</span>
                          <span><span className="font-bold">{igData.collaboration_stats?.solo_posts ?? 0}</span> solo</span>
                          <span className="font-bold text-accent-lime">{igData.collaboration_stats?.collaboration_rate ?? "0%"}</span>
                        </div>
                      </div>
                    </div>

                    {/* Frequency Status */}
                    {igData.compliance_analysis?.post_frequency && (
                      <div className="bg-[#0a0a0a] rounded-xl px-3 py-2.5 mt-2 text-[11px]">
                        <div className="text-text-tertiary font-bold mb-1.5">Frequency</div>
                        <div className={`font-bold ${igData.compliance_analysis.post_frequency.status === "met" ? "text-success" : "text-warning"}`}>
                          {igData.compliance_analysis.post_frequency.delivered} <span className="text-text-tertiary font-normal">/ {igData.compliance_analysis.post_frequency.required} req.</span>
                        </div>
                      </div>
                    )}

                    {/* Met / Missing chips */}
                    {(igData.compliance_analysis?.deliverables_met?.length || igData.compliance_analysis?.deliverables_missing?.length) ? (
                      <div className="flex flex-wrap gap-1.5 mt-3">
                        {igData.compliance_analysis.deliverables_met?.slice(0, 2).map((d, i) => (
                          <span key={i} className="text-[10px] font-semibold bg-success/10 text-success px-2 py-0.5 rounded-full">✓ {d}</span>
                        ))}
                        {igData.compliance_analysis.deliverables_missing?.slice(0, 2).map((d, i) => (
                          <span key={i} className="text-[10px] font-semibold bg-danger/10 text-danger px-2 py-0.5 rounded-full">✗ {d}</span>
                        ))}
                      </div>
                    ) : null}
                  </BentoCard>
                );
              })()}

              {/* TikTok */}
              {ttData && (() => {
                const required = ttRequired;
                const delivered = ttPosts;
                const pct = required > 0 ? Math.round((delivered / required) * 100) : 0;
                return (
                  <BentoCard delay={0.15} gradient="bg-gradient-to-br from-[#00f2ea]/10 to-[#121212]" className="p-6">
                    <div className="flex items-center justify-between mb-5">
                      <div className="flex items-center gap-3">
                        <div className="w-11 h-11 rounded-2xl bg-tiktok/20 flex items-center justify-center text-tiktok">
                          <TikTokIcon className="w-5 h-5" />
                        </div>
                        <div>
                          <div className="font-semibold text-base">TikTok</div>
                          {selectedClient?.tiktok && (
                            <div className="text-[11px] text-text-tertiary">@{selectedClient.tiktok}</div>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`text-xs font-bold px-2.5 py-1 rounded-full ${getHeatBgClass(ttScore)}`}>
                          AI Compliance score is at {ttScore}%
                        </span>
                        {selectedClient?.tiktok && (
                          <a href={`https://tiktok.com/@${selectedClient.tiktok}`} target="_blank" rel="noopener noreferrer" className="w-8 h-8 rounded-full flex items-center justify-center text-text-tertiary hover:text-tiktok hover:bg-tiktok/10 transition-all" title="Open TikTok">
                            <ExternalLink className="w-4 h-4" />
                          </a>
                        )}
                      </div>
                    </div>

                    {/* Delivery progress */}
                    <div className="bg-[#0a0a0a] rounded-2xl p-4 mb-3">
                      <div className="flex justify-between items-baseline mb-2">
                        <span className="text-xs text-text-tertiary font-medium">Deliverables</span>
                        <span className={`font-[family-name:var(--font-space-grotesk)] text-lg font-bold ${getHeatTextClass(pct)}`}>
                          {pct > 0 ? `${pct}%` : "—"}
                        </span>
                      </div>
                      <div className="h-2 bg-[#141414] rounded-full overflow-hidden mb-2">
                        <motion.div className="h-full rounded-full" style={{ background: getHeatColor(pct) }} initial={{ width: 0 }} animate={{ width: `${Math.min(pct, 100)}%` }} transition={{ duration: 0.8, delay: 0.2 }} />
                      </div>
                      <div className="flex justify-between text-[11px]">
                        <span className="text-text-tertiary">{delivered} delivered</span>
                        <span className="text-text-tertiary">{required > 0 ? `${required} required` : "No target"}</span>
                      </div>
                      {pct > 100 && (
                        <div className="mt-2 text-[10px] font-bold text-accent-blue bg-accent-blue/10 px-2 py-0.5 rounded-full inline-block">
                          ⚡ Overachieved by {pct - 100}%
                        </div>
                      )}
                    </div>

                    {/* Content breakdown */}
                    <div className="grid grid-cols-2 gap-2 text-[11px]">
                      <div className="bg-[#0a0a0a] rounded-xl px-3 py-2.5">
                        <div className="text-text-tertiary flex items-center gap-1"><Film className="w-3 h-3" /> Videos</div>
                        <div className="font-[family-name:var(--font-space-grotesk)] text-lg font-bold mt-0.5">{ttData.content_breakdown?.videos ?? 0}</div>
                      </div>
                      <div className="bg-[#0a0a0a] rounded-xl px-3 py-2.5">
                        <div className="text-text-tertiary flex items-center gap-1"><ImageIcon className="w-3 h-3" /> Images</div>
                        <div className="font-[family-name:var(--font-space-grotesk)] text-lg font-bold mt-0.5">{ttData.content_breakdown?.images ?? 0}</div>
                      </div>
                    </div>

                    {/* Frequency Status */}
                    {ttData.compliance_analysis?.post_frequency && (
                      <div className="bg-[#0a0a0a] rounded-xl px-3 py-2.5 mt-2 text-[11px]">
                        <div className="text-text-tertiary font-bold mb-1.5">Frequency</div>
                        <div className={`font-bold ${ttData.compliance_analysis.post_frequency.status === "met" ? "text-success" : "text-warning"}`}>
                          {ttData.compliance_analysis.post_frequency.delivered} <span className="text-text-tertiary font-normal">/ {ttData.compliance_analysis.post_frequency.required} req.</span>
                        </div>
                      </div>
                    )}

                    {/* Met / Missing chips */}
                    {(ttData.compliance_analysis?.deliverables_met?.length || ttData.compliance_analysis?.deliverables_missing?.length) ? (
                      <div className="flex flex-wrap gap-1.5 mt-3">
                        {ttData.compliance_analysis.deliverables_met?.slice(0, 2).map((d, i) => (
                          <span key={i} className="text-[10px] font-semibold bg-success/10 text-success px-2 py-0.5 rounded-full">✓ {d}</span>
                        ))}
                        {ttData.compliance_analysis.deliverables_missing?.slice(0, 2).map((d, i) => (
                          <span key={i} className="text-[10px] font-semibold bg-danger/10 text-danger px-2 py-0.5 rounded-full">✗ {d}</span>
                        ))}
                      </div>
                    ) : null}
                  </BentoCard>
                );
              })()}
            </div>
          </div>

          {/* ROW 3: Content Activity — full width calendar */}
          <BentoCard delay={0.15} gradient="bg-gradient-to-br from-[#1a1a1a] to-[#0a0a0a]" className="p-5 sm:p-7">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-5">
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-text-tertiary block mb-1">
                  Content Activity
                </span>
                <span className="font-[family-name:var(--font-space-grotesk)] text-lg sm:text-2xl font-bold text-white">
                  {dateRange.start.split("-").slice(1).join("/")} &mdash; {dateRange.end.split("-").slice(1).join("/")}
                </span>
              </div>
              <div className="sm:text-right">
                <div className="text-sm font-semibold text-text-secondary">
                  {selectedClient?.name}
                </div>
                <div className="text-[10px] text-text-tertiary mt-0.5">
                  {totalPosts} posts delivered
                </div>
              </div>
            </div>

            {/* Target progress bars */}
            {(() => {
              const totalPct = totalRequired > 0 ? Math.round((totalPosts / totalRequired) * 100) : 0;

              return (
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-2 sm:gap-3 mb-5">
                  {fbData && (
                    <div className="bg-[#0e0e0e] rounded-xl px-3 py-2.5">
                      <div className="flex items-center justify-between text-[10px] mb-1.5">
                        <span className="flex items-center gap-1.5 text-text-tertiary font-medium"><FacebookIcon className="w-3 h-3 text-facebook" /> FB</span>
                        <span className={`font-bold ${getHeatTextClass(fbRequired > 0 ? Math.round((fbPosts / fbRequired) * 100) : 0)}`}>
                          {fbPosts}/{fbRequired || "—"}
                        </span>
                      </div>
                      <div className="h-1.5 bg-[#1a1a1a] rounded-full overflow-hidden">
                        <motion.div className="h-full rounded-full bg-facebook" initial={{ width: 0 }} animate={{ width: `${Math.min(fbRequired > 0 ? (fbPosts / fbRequired) * 100 : 0, 100)}%` }} transition={{ duration: 0.8 }} />
                      </div>
                      {fbRequired > 0 && fbPosts > fbRequired && (
                        <div className="text-[9px] font-bold text-accent-blue mt-1">+{fbPosts - fbRequired} over target</div>
                      )}
                    </div>
                  )}
                  {igData && (
                    <div className="bg-[#0e0e0e] rounded-xl px-3 py-2.5">
                      <div className="flex items-center justify-between text-[10px] mb-1.5">
                        <span className="flex items-center gap-1.5 text-text-tertiary font-medium"><InstagramIcon className="w-3 h-3 text-instagram" /> IG</span>
                        <span className={`font-bold ${getHeatTextClass(igRequired > 0 ? Math.round((igPosts / igRequired) * 100) : 0)}`}>
                          {igPosts}/{igRequired || "—"}
                        </span>
                      </div>
                      <div className="h-1.5 bg-[#1a1a1a] rounded-full overflow-hidden">
                        <motion.div className="h-full rounded-full bg-instagram" initial={{ width: 0 }} animate={{ width: `${Math.min(igRequired > 0 ? (igPosts / igRequired) * 100 : 0, 100)}%` }} transition={{ duration: 0.8, delay: 0.1 }} />
                      </div>
                      {igRequired > 0 && igPosts > igRequired && (
                        <div className="text-[9px] font-bold text-accent-blue mt-1">+{igPosts - igRequired} over target</div>
                      )}
                    </div>
                  )}
                  {ttData && (
                    <div className="bg-[#0e0e0e] rounded-xl px-3 py-2.5">
                      <div className="flex items-center justify-between text-[10px] mb-1.5">
                        <span className="flex items-center gap-1.5 text-text-tertiary font-medium"><TikTokIcon className="w-3 h-3 text-tiktok" /> TT</span>
                        <span className={`font-bold ${getHeatTextClass(ttRequired > 0 ? Math.round((ttPosts / ttRequired) * 100) : 0)}`}>
                          {ttPosts}/{ttRequired || "—"}
                        </span>
                      </div>
                      <div className="h-1.5 bg-[#1a1a1a] rounded-full overflow-hidden">
                        <motion.div className="h-full rounded-full bg-tiktok" initial={{ width: 0 }} animate={{ width: `${Math.min(ttRequired > 0 ? (ttPosts / ttRequired) * 100 : 0, 100)}%` }} transition={{ duration: 0.8, delay: 0.2 }} />
                      </div>
                      {ttRequired > 0 && ttPosts > ttRequired && (
                        <div className="text-[9px] font-bold text-accent-blue mt-1">+{ttPosts - ttRequired} over target</div>
                      )}
                    </div>
                  )}
                  <div className="bg-[#0e0e0e] rounded-xl px-3 py-2.5">
                    <div className="flex items-center justify-between text-[10px] mb-1.5">
                      <span className="text-text-tertiary font-bold">TOTAL</span>
                      <span className={`font-bold ${getHeatTextClass(totalPct)}`}>
                        {totalPct > 0 ? `${totalPct}%` : "—"}
                      </span>
                    </div>
                    <div className="h-1.5 bg-[#1a1a1a] rounded-full overflow-hidden">
                      <motion.div className="h-full rounded-full" style={{ background: getHeatColor(totalPct) }} initial={{ width: 0 }} animate={{ width: `${Math.min(totalPct, 100)}%` }} transition={{ duration: 0.8, delay: 0.3 }} />
                    </div>
                    {totalPct > 100 && (
                      <div className="text-[9px] font-bold text-accent-blue mt-1">⚡ {totalPct}% of target</div>
                    )}
                  </div>
                </div>
              );
            })()}

            {/* Date-based calendar grid */}
            {(() => {
              const FB_COLOR = "#1877f2";
              const IG_COLOR = "#e1306c";
              const TT_COLOR = "#00f2ea";

              const startD = new Date(dateRange.start + "T00:00:00");
              const endD = new Date(dateRange.end + "T00:00:00");
              const totalDays = Math.max(1, Math.round((endD.getTime() - startD.getTime()) / 86400000) + 1);

              interface DayCell { date: Date; fb: boolean; ig: boolean; tt: boolean }
              const dayCells: DayCell[] = Array.from({ length: totalDays }, (_, i) => {
                const d = new Date(startD);
                d.setDate(d.getDate() + i);
                return { date: d, fb: false, ig: false, tt: false };
              });

              // Spread posts evenly across the date range
              const spreadPosts = (count: number, key: "fb" | "ig" | "tt") => {
                if (count <= 0 || dayCells.length === 0) return;
                const step = dayCells.length / count;
                for (let p = 0; p < count; p++) {
                  const idx = Math.min(Math.floor(p * step + step * 0.3), dayCells.length - 1);
                  dayCells[idx][key] = true;
                }
              };
              spreadPosts(fbPosts, "fb");
              spreadPosts(igPosts, "ig");
              spreadPosts(ttPosts, "tt");

              // Pad start to align with weekday (0=Sun)
              const firstDayOfWeek = dayCells[0]?.date.getDay() ?? 0;
              const paddedCells: (DayCell | null)[] = [...Array(firstDayOfWeek).fill(null), ...dayCells];
              const weekdays = ["S", "M", "T", "W", "T", "F", "S"];

              return (
                <>
                  {/* Weekday headers */}
                  <div className="grid gap-1 sm:gap-1.5 mb-1 sm:mb-1.5" style={{ gridTemplateColumns: "repeat(7, minmax(0, 1fr))" }}>
                    {weekdays.map((d, i) => (
                      <div key={i} className="text-center text-[8px] sm:text-[9px] font-bold text-text-tertiary/50 uppercase">{d}</div>
                    ))}
                  </div>

                  {/* Calendar grid */}
                  <div className="overflow-y-auto max-h-[220px] sm:max-h-[280px] pr-1 [&::-webkit-scrollbar]:w-1.5 [&::-webkit-scrollbar-thumb]:rounded-full [&::-webkit-scrollbar-thumb]:bg-white/10">
                    <div className="grid gap-1 sm:gap-1.5" style={{ gridTemplateColumns: "repeat(7, minmax(0, 1fr))" }}>
                      {paddedCells.map((cell, i) => {
                        if (!cell) return <div key={`pad-${i}`} className="aspect-square" />;

                        const platforms = [cell.fb, cell.ig, cell.tt].filter(Boolean).length;
                        const dateLabel = cell.date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
                        const dayNum = cell.date.getDate();

                        // Build color style for the cell
                        let bgStyle: React.CSSProperties = {};
                        let cellClass = "bg-[#111] hover:bg-[#1a1a1a]";

                        if (platforms === 1) {
                          bgStyle = { background: cell.fb ? FB_COLOR : cell.ig ? IG_COLOR : TT_COLOR };
                          cellClass = "hover:brightness-125";
                        } else if (platforms === 2) {
                          const colors = [cell.fb && FB_COLOR, cell.ig && IG_COLOR, cell.tt && TT_COLOR].filter(Boolean) as string[];
                          bgStyle = { background: `linear-gradient(135deg, ${colors[0]} 50%, ${colors[1]} 50%)` };
                          cellClass = "hover:brightness-125 ring-1 ring-white/20";
                        } else if (platforms === 3) {
                          bgStyle = { background: `linear-gradient(135deg, ${FB_COLOR} 33%, ${IG_COLOR} 33% 66%, ${TT_COLOR} 66%)`, boxShadow: "0 0 8px rgba(255,255,255,0.15)" };
                          cellClass = "hover:brightness-125 ring-1 ring-white/30";
                        }

                        const platformNames = [cell.fb && "Facebook", cell.ig && "Instagram", cell.tt && "TikTok"].filter(Boolean);
                        const tooltipText = platformNames.length > 0
                          ? `${dateLabel} · ${platformNames.join(" + ")}`
                          : `${dateLabel} · No posts`;

                        return (
                          <div key={i} className="group relative">
                            <div
                              className={`aspect-square rounded-lg transition-all cursor-default flex items-center justify-center ${cellClass}`}
                              style={bgStyle}
                            >
                              <span className={`text-[8px] font-bold leading-none ${platforms > 0 ? "text-white/80" : "text-white/15"}`}>
                                {dayNum}
                              </span>
                            </div>
                            <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2.5 py-1.5 rounded-lg bg-[#1a1a1a] border border-white/[0.08] text-[10px] font-semibold text-text-primary whitespace-nowrap opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-150 z-10 shadow-xl pointer-events-none">
                              {tooltipText}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Legend */}
                  <div className="flex flex-wrap items-center gap-3 sm:gap-4 mt-3 sm:mt-4 text-[9px] sm:text-[10px] font-semibold text-text-tertiary">
                    <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded" style={{ background: FB_COLOR }} /> Facebook</span>
                    <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded" style={{ background: IG_COLOR }} /> Instagram</span>
                    <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded" style={{ background: TT_COLOR }} /> TikTok</span>
                    <span className="flex items-center gap-1.5">
                      <span className="w-3 h-3 rounded" style={{ background: `linear-gradient(135deg, ${FB_COLOR} 50%, ${IG_COLOR} 50%)` }} />
                      Multi-platform
                    </span>
                    <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded bg-[#111]" /> No posts</span>
                  </div>
                </>
              );
            })()}
          </BentoCard>

          {/* ROW 4: AI Analysis */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Zap className="w-4 h-4 text-accent-lime" />
              <h2 className="font-[family-name:var(--font-space-grotesk)] text-xl font-bold tracking-tight">
                AI Analysis
              </h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <AnalysisPanel platform="facebook" analysis={fbData?.compliance_analysis ?? null} />
              <AnalysisPanel platform="instagram" analysis={igData?.compliance_analysis ?? null} />
              <AnalysisPanel platform="tiktok" analysis={ttData?.compliance_analysis ?? null} />
            </div>
          </div>

        </div>
      )}
    </div>
  );
}
