"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { RefreshCw, ArrowUpRight, BarChart3, Target, Users, Zap, Film, Image as ImageIcon, Layers, Handshake, ExternalLink, ChevronDown, Calendar } from "lucide-react";
import { motion } from "framer-motion";

import { BentoCard } from "@/components/ui/bento-card";
import { MetricRing } from "@/components/ui/metric-ring";
import { PlatformCard } from "@/components/ui/platform-card";
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
import { getComplianceStatus, getDefaultDateRange } from "@/lib/utils";

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

  return (
    <div className="min-h-screen pb-24 lg:pb-6">
      {/* Controls Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 px-5 py-4 sticky top-[72px] z-30 bg-bg-primary/60 backdrop-blur-2xl border-b border-white/[0.04]">
        {/* Client Select */}
        <div className="relative flex-[2] min-w-0 group">
          <div className="absolute left-4 top-1/2 -translate-y-1/2 pointer-events-none">
            <Users className="w-4 h-4 text-text-tertiary group-focus-within:text-accent-lime transition-colors" />
          </div>
          <select
            className="w-full bg-white/[0.04] border border-white/[0.06] text-text-primary rounded-2xl pl-10 pr-10 py-3 text-sm font-semibold outline-none focus:border-accent-lime/40 focus:bg-white/[0.06] transition-all appearance-none cursor-pointer"
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
        <div className="px-5 py-6 space-y-5 max-w-[1400px] mx-auto">

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
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">

            {/* HERO CARD - lime bg */}
            <BentoCard
              className="lg:col-span-4 p-7 relative overflow-hidden min-h-[340px] flex flex-col justify-between"
              gradient="bg-gradient-to-br from-[#ccf381] to-[#a8d84e]"
              delay={0}
            >
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <Zap className="w-5 h-5 text-[#050505]" />
                  <span className="text-[11px] font-bold uppercase tracking-widest text-[#050505]/60">
                    Compliance Score
                  </span>
                </div>
                <div className="font-[family-name:var(--font-space-grotesk)] text-[80px] lg:text-[96px] font-bold leading-[0.85] tracking-tighter text-[#050505]">
                  {avgScore}%
                </div>
                <div className="mt-2 text-lg font-bold text-[#050505]/80">
                  {getComplianceStatus(avgScore)}
                </div>
              </div>
              <div className="mt-4 bg-[#050505]/10 backdrop-blur-sm rounded-2xl p-4">
                <p className="text-sm font-semibold text-[#050505]/70">
                  {activePlatforms} active platform{activePlatforms !== 1 ? "s" : ""} &bull; {totalPosts} deliverables tracked
                </p>
              </div>
            </BentoCard>

            {/* PLATFORM SCORE RINGS */}
            <BentoCard className="lg:col-span-5 p-7" delay={0.05}>
              <div className="flex items-center justify-between mb-8">
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
              <div className="flex items-center justify-around">
                <MetricRing score={fbScore} label="Facebook" color="var(--color-facebook)" size={120} />
                <MetricRing score={igScore} label="Instagram" color="var(--color-instagram)" size={120} />
                <MetricRing score={ttScore} label="TikTok" color="var(--color-tiktok)" size={120} />
              </div>
            </BentoCard>

            {/* RIGHT stacked */}
            <div className="lg:col-span-3 grid grid-rows-2 gap-5">
              <BentoCard
                delay={0.1}
                gradient="bg-gradient-to-br from-[#7928ca] to-[#4c1d95]"
                className="p-6 flex flex-col justify-between min-h-[160px]"
              >
                <span className="text-[10px] font-bold uppercase tracking-widest text-white/50">
                  Total Deliverables
                </span>
                <div>
                  <div className="font-[family-name:var(--font-space-grotesk)] text-5xl font-bold text-white leading-none">
                    {totalPosts}
                  </div>
                  <span className="text-sm text-white/50 font-medium">pieces delivered</span>
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

          {/* ROW 2: Platform Stat Cards with solid backgrounds */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Facebook */}
            <BentoCard delay={0.05} gradient="bg-gradient-to-br from-[#1877f2]/20 to-[#121212]" className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="w-10 h-10 rounded-2xl bg-facebook/20 flex items-center justify-center text-facebook">
                  <FacebookIcon className="w-5 h-5" />
                </div>
                {selectedClient?.facebook && (
                  <a href={`https://facebook.com/${selectedClient.facebook}`} target="_blank" rel="noopener noreferrer" className="w-8 h-8 rounded-full flex items-center justify-center text-text-tertiary hover:text-facebook hover:bg-facebook/10 transition-all" title="Open Facebook">
                    <ExternalLink className="w-4 h-4" />
                  </a>
                )}
              </div>
              <div className="font-[family-name:var(--font-space-grotesk)] text-4xl font-bold mb-1">
                {fbPosts}
              </div>
              <div className="text-xs font-bold uppercase tracking-wider text-text-tertiary mb-3">
                Facebook Posts
              </div>
              {fbData && (
                <div className="text-[11px] text-text-secondary border-t border-border pt-3 space-y-1">
                  <div className="flex justify-between">
                    <span>Static Posts</span>
                    <span className="font-bold text-text-primary">{fbData.content_breakdown?.posts ?? 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Videos/Reels</span>
                    <span className="font-bold text-text-primary">{fbData.content_breakdown?.videos ?? 0}</span>
                  </div>
                </div>
              )}
            </BentoCard>

            {/* Instagram */}
            <BentoCard delay={0.1} gradient="bg-gradient-to-br from-[#e1306c]/20 to-[#121212]" className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="w-10 h-10 rounded-2xl bg-instagram/20 flex items-center justify-center text-instagram">
                  <InstagramIcon className="w-5 h-5" />
                </div>
                {selectedClient?.instagram && (
                  <a href={`https://instagram.com/${selectedClient.instagram}`} target="_blank" rel="noopener noreferrer" className="w-8 h-8 rounded-full flex items-center justify-center text-text-tertiary hover:text-instagram hover:bg-instagram/10 transition-all" title="Open Instagram">
                    <ExternalLink className="w-4 h-4" />
                  </a>
                )}
              </div>
              <div className="font-[family-name:var(--font-space-grotesk)] text-4xl font-bold mb-1">
                {igPosts}
              </div>
              <div className="text-xs font-bold uppercase tracking-wider text-text-tertiary mb-3">
                Instagram Posts
              </div>
              {igData && (
                <div className="text-[11px] text-text-secondary border-t border-border pt-3 space-y-1">
                  <div className="flex justify-between">
                    <span className="flex items-center gap-1"><Layers className="w-3 h-3" /> Carousel</span>
                    <span className="font-bold text-text-primary">{igData.content_types?.carousel ?? 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="flex items-center gap-1"><ImageIcon className="w-3 h-3" /> Images</span>
                    <span className="font-bold text-text-primary">{igData.content_types?.image ?? 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="flex items-center gap-1"><Film className="w-3 h-3" /> Videos</span>
                    <span className="font-bold text-text-primary">{igData.content_types?.video ?? 0}</span>
                  </div>
                </div>
              )}
            </BentoCard>

            {/* TikTok */}
            <BentoCard delay={0.15} gradient="bg-gradient-to-br from-[#00f2ea]/15 to-[#121212]" className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="w-10 h-10 rounded-2xl bg-tiktok/20 flex items-center justify-center text-tiktok">
                  <TikTokIcon className="w-5 h-5" />
                </div>
                {selectedClient?.tiktok && (
                  <a href={`https://tiktok.com/@${selectedClient.tiktok}`} target="_blank" rel="noopener noreferrer" className="w-8 h-8 rounded-full flex items-center justify-center text-text-tertiary hover:text-tiktok hover:bg-tiktok/10 transition-all" title="Open TikTok">
                    <ExternalLink className="w-4 h-4" />
                  </a>
                )}
              </div>
              <div className="font-[family-name:var(--font-space-grotesk)] text-4xl font-bold mb-1">
                {ttPosts}
              </div>
              <div className="text-xs font-bold uppercase tracking-wider text-text-tertiary mb-3">
                TikTok Videos
              </div>
              {ttData && (
                <div className="text-[11px] text-text-secondary border-t border-border pt-3 space-y-1">
                  <div className="flex justify-between">
                    <span className="flex items-center gap-1"><Film className="w-3 h-3" /> Videos</span>
                    <span className="font-bold text-text-primary">{ttData.content_breakdown?.videos ?? 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="flex items-center gap-1"><ImageIcon className="w-3 h-3" /> Images</span>
                    <span className="font-bold text-text-primary">{ttData.content_breakdown?.images ?? 0}</span>
                  </div>
                </div>
              )}
            </BentoCard>

            {/* Collabs - white card like inspo */}
            <BentoCard delay={0.2} gradient="bg-white" className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="w-10 h-10 rounded-2xl bg-black flex items-center justify-center">
                  <Handshake className="w-5 h-5 text-white" />
                </div>
                <ArrowUpRight className="w-4 h-4 text-black/30" />
              </div>
              <div className="font-[family-name:var(--font-space-grotesk)] text-4xl font-bold mb-1 text-black">
                {igData?.collaboration_stats?.collaborative_posts ?? 0}
              </div>
              <div className="text-xs font-bold uppercase tracking-wider text-black/40 mb-3">
                Collaborations
              </div>
              {igData && (
                <div className="text-[11px] text-black/50 border-t border-black/10 pt-3 space-y-1">
                  <div className="flex justify-between">
                    <span>Solo Posts</span>
                    <span className="font-bold text-black">{igData.collaboration_stats?.solo_posts ?? 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Collab Rate</span>
                    <span className="font-bold text-black">{igData.collaboration_stats?.collaboration_rate ?? "0%"}</span>
                  </div>
                </div>
              )}
            </BentoCard>
          </div>

          {/* ROW 3: Compliance Progress + Activity */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            {/* Compliance Breakdown — richer contract context */}
            <BentoCard delay={0.1} className="p-7">
              <div className="flex items-center justify-between mb-6">
                <h3 className="font-[family-name:var(--font-space-grotesk)] text-xl font-bold">
                  Compliance Breakdown
                </h3>
                <span className="text-xs text-text-tertiary bg-white/[0.04] border border-white/[0.06] px-3 py-1 rounded-full">
                  Score / 100
                </span>
              </div>
              <div className="space-y-6">
                {fbData && (
                  <div>
                    <div className="flex items-center gap-3 mb-2">
                      <div className="w-8 h-8 rounded-full bg-facebook/10 flex items-center justify-center flex-shrink-0">
                        <FacebookIcon className="w-4 h-4 text-facebook" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex justify-between items-baseline mb-1">
                          <span className="font-semibold text-sm">Facebook</span>
                          <span className="font-[family-name:var(--font-space-grotesk)] text-sm font-bold">{fbScore}%</span>
                        </div>
                        <div className="h-2.5 bg-[#0a0a0a] rounded-full overflow-hidden">
                          <motion.div className="h-full rounded-full bg-facebook" initial={{ width: 0 }} animate={{ width: `${fbScore}%` }} transition={{ duration: 1 }} />
                        </div>
                      </div>
                    </div>
                    {/* Contract context */}
                    <div className="ml-11 grid grid-cols-2 gap-2 mt-2">
                      <div className="bg-[#0a0a0a] rounded-xl px-3 py-2 text-[11px]">
                        <div className="text-text-tertiary mb-0.5">Posts delivered</div>
                        <div className="font-bold text-text-primary">{fbData.content_breakdown?.posts ?? 0} posts · {fbData.content_breakdown?.videos ?? 0} videos</div>
                      </div>
                      <div className="bg-[#0a0a0a] rounded-xl px-3 py-2 text-[11px]">
                        <div className="text-text-tertiary mb-0.5">Freq. status</div>
                        <div className={`font-bold ${fbData.compliance_analysis?.post_frequency?.status === "met" ? "text-success" : "text-warning"}`}>
                          {fbData.compliance_analysis?.post_frequency?.delivered ?? "—"} <span className="text-text-tertiary font-normal">/ required {fbData.compliance_analysis?.post_frequency?.required ?? "—"}</span>
                        </div>
                      </div>
                    </div>
                    {/* Met / Missing chips */}
                    {(fbData.compliance_analysis?.deliverables_met?.length || fbData.compliance_analysis?.deliverables_missing?.length) ? (
                      <div className="ml-11 flex flex-wrap gap-1.5 mt-2">
                        {fbData.compliance_analysis.deliverables_met?.slice(0, 2).map((d, i) => (
                          <span key={i} className="text-[10px] font-semibold bg-success/10 text-success px-2 py-0.5 rounded-full">✓ {d}</span>
                        ))}
                        {fbData.compliance_analysis.deliverables_missing?.slice(0, 2).map((d, i) => (
                          <span key={i} className="text-[10px] font-semibold bg-danger/10 text-danger px-2 py-0.5 rounded-full">✗ {d}</span>
                        ))}
                      </div>
                    ) : null}
                  </div>
                )}
                {igData && (
                  <div>
                    <div className="flex items-center gap-3 mb-2">
                      <div className="w-8 h-8 rounded-full bg-instagram/10 flex items-center justify-center flex-shrink-0">
                        <InstagramIcon className="w-4 h-4 text-instagram" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex justify-between items-baseline mb-1">
                          <span className="font-semibold text-sm">Instagram</span>
                          <span className="font-[family-name:var(--font-space-grotesk)] text-sm font-bold">{igScore}%</span>
                        </div>
                        <div className="h-2.5 bg-[#0a0a0a] rounded-full overflow-hidden">
                          <motion.div className="h-full rounded-full bg-instagram" initial={{ width: 0 }} animate={{ width: `${igScore}%` }} transition={{ duration: 1, delay: 0.1 }} />
                        </div>
                      </div>
                    </div>
                    <div className="ml-11 grid grid-cols-2 gap-2 mt-2">
                      <div className="bg-[#0a0a0a] rounded-xl px-3 py-2 text-[11px]">
                        <div className="text-text-tertiary mb-0.5">Posts delivered</div>
                        <div className="font-bold text-text-primary">{igData.content_types?.carousel ?? 0} carousel · {igData.content_types?.video ?? 0} video · {igData.content_types?.image ?? 0} img</div>
                      </div>
                      <div className="bg-[#0a0a0a] rounded-xl px-3 py-2 text-[11px]">
                        <div className="text-text-tertiary mb-0.5">Freq. status</div>
                        <div className={`font-bold ${igData.compliance_analysis?.post_frequency?.status === "met" ? "text-success" : "text-warning"}`}>
                          {igData.compliance_analysis?.post_frequency?.delivered ?? "—"} <span className="text-text-tertiary font-normal">/ required {igData.compliance_analysis?.post_frequency?.required ?? "—"}</span>
                        </div>
                      </div>
                    </div>
                    {(igData.compliance_analysis?.deliverables_met?.length || igData.compliance_analysis?.deliverables_missing?.length) ? (
                      <div className="ml-11 flex flex-wrap gap-1.5 mt-2">
                        {igData.compliance_analysis.deliverables_met?.slice(0, 2).map((d, i) => (
                          <span key={i} className="text-[10px] font-semibold bg-success/10 text-success px-2 py-0.5 rounded-full">✓ {d}</span>
                        ))}
                        {igData.compliance_analysis.deliverables_missing?.slice(0, 2).map((d, i) => (
                          <span key={i} className="text-[10px] font-semibold bg-danger/10 text-danger px-2 py-0.5 rounded-full">✗ {d}</span>
                        ))}
                      </div>
                    ) : null}
                  </div>
                )}
                {ttData && (
                  <div>
                    <div className="flex items-center gap-3 mb-2">
                      <div className="w-8 h-8 rounded-full bg-tiktok/10 flex items-center justify-center flex-shrink-0">
                        <TikTokIcon className="w-4 h-4 text-tiktok" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex justify-between items-baseline mb-1">
                          <span className="font-semibold text-sm">TikTok</span>
                          <span className="font-[family-name:var(--font-space-grotesk)] text-sm font-bold">{ttScore}%</span>
                        </div>
                        <div className="h-2.5 bg-[#0a0a0a] rounded-full overflow-hidden">
                          <motion.div className="h-full rounded-full bg-tiktok" initial={{ width: 0 }} animate={{ width: `${ttScore}%` }} transition={{ duration: 1, delay: 0.2 }} />
                        </div>
                      </div>
                    </div>
                    <div className="ml-11 grid grid-cols-2 gap-2 mt-2">
                      <div className="bg-[#0a0a0a] rounded-xl px-3 py-2 text-[11px]">
                        <div className="text-text-tertiary mb-0.5">Posts delivered</div>
                        <div className="font-bold text-text-primary">{ttData.content_breakdown?.videos ?? 0} videos · {ttData.content_breakdown?.images ?? 0} images</div>
                      </div>
                      <div className="bg-[#0a0a0a] rounded-xl px-3 py-2 text-[11px]">
                        <div className="text-text-tertiary mb-0.5">Freq. status</div>
                        <div className={`font-bold ${ttData.compliance_analysis?.post_frequency?.status === "met" ? "text-success" : "text-warning"}`}>
                          {ttData.compliance_analysis?.post_frequency?.delivered ?? "—"} <span className="text-text-tertiary font-normal">/ required {ttData.compliance_analysis?.post_frequency?.required ?? "—"}</span>
                        </div>
                      </div>
                    </div>
                    {(ttData.compliance_analysis?.deliverables_met?.length || ttData.compliance_analysis?.deliverables_missing?.length) ? (
                      <div className="ml-11 flex flex-wrap gap-1.5 mt-2">
                        {ttData.compliance_analysis.deliverables_met?.slice(0, 2).map((d, i) => (
                          <span key={i} className="text-[10px] font-semibold bg-success/10 text-success px-2 py-0.5 rounded-full">✓ {d}</span>
                        ))}
                        {ttData.compliance_analysis.deliverables_missing?.slice(0, 2).map((d, i) => (
                          <span key={i} className="text-[10px] font-semibold bg-danger/10 text-danger px-2 py-0.5 rounded-full">✗ {d}</span>
                        ))}
                      </div>
                    ) : null}
                  </div>
                )}
              </div>
            </BentoCard>

            <BentoCard delay={0.15} gradient="bg-gradient-to-br from-[#1a1a1a] to-[#0a0a0a]" className="p-7">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <span className="text-xs font-bold uppercase tracking-wider text-text-tertiary block mb-1">
                    Content Activity
                  </span>
                  <span className="font-[family-name:var(--font-space-grotesk)] text-2xl font-bold text-white">
                    {dateRange.start.split("-").slice(1).join("/")} &mdash; {dateRange.end.split("-").slice(1).join("/")}
                  </span>
                </div>
                <div className="text-right">
                  <div className="text-sm font-semibold text-text-secondary">
                    {selectedClient?.name}
                  </div>
                  <div className="text-[10px] text-text-tertiary mt-0.5">
                    {totalPosts} posts delivered
                  </div>
                </div>
              </div>

              {/* Summary chips */}
              {(() => {
                const totalSlots = Math.max(28, totalPosts + Math.ceil(totalPosts * 0.2));
                return (
                  <>
                    <div className="flex flex-wrap gap-2 mb-4">
                      <span className="inline-flex items-center gap-1.5 text-[10px] font-bold bg-facebook/15 text-facebook px-2.5 py-1 rounded-full">
                        <span className="w-1.5 h-1.5 rounded-full bg-facebook" /> {fbPosts} FB
                      </span>
                      <span className="inline-flex items-center gap-1.5 text-[10px] font-bold bg-instagram/15 text-instagram px-2.5 py-1 rounded-full">
                        <span className="w-1.5 h-1.5 rounded-full bg-instagram" /> {igPosts} IG
                      </span>
                      <span className="inline-flex items-center gap-1.5 text-[10px] font-bold bg-tiktok/15 text-tiktok px-2.5 py-1 rounded-full">
                        <span className="w-1.5 h-1.5 rounded-full bg-tiktok" /> {ttPosts} TT
                      </span>
                      <span className="inline-flex items-center gap-1.5 text-[10px] font-bold bg-white/5 text-text-tertiary px-2.5 py-1 rounded-full">
                        {Math.max(0, totalSlots - totalPosts)} empty
                      </span>
                    </div>

                    {/* Scrollable grid */}
                    <div className="overflow-y-auto max-h-[220px] pr-1 [&::-webkit-scrollbar]:w-1.5 [&::-webkit-scrollbar-thumb]:rounded-full [&::-webkit-scrollbar-thumb]:bg-white/10">
                      <div className="grid gap-2" style={{ gridTemplateColumns: "repeat(7, minmax(0, 1fr))" }}>
                        {Array.from({ length: totalSlots }).map((_, i) => {
                          const fbActive = i < fbPosts;
                          const igActive = i >= fbPosts && i < fbPosts + igPosts;
                          const ttActive = i >= fbPosts + igPosts && i < totalPosts;
                          const platformLabel = fbActive ? "Facebook" : igActive ? "Instagram" : ttActive ? "TikTok" : "Empty";
                          const postNum = fbActive ? i + 1 : igActive ? i - fbPosts + 1 : ttActive ? i - fbPosts - igPosts + 1 : 0;
                          return (
                            <div key={i} className="group relative">
                              <div
                                className={`aspect-square rounded-lg transition-all cursor-default ${
                                  fbActive ? "bg-facebook hover:brightness-125" :
                                  igActive ? "bg-instagram hover:brightness-125" :
                                  ttActive ? "bg-tiktok hover:brightness-125" :
                                  "bg-[#1a1a1a] hover:bg-[#222]"
                                }`}
                              />
                              <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2.5 py-1.5 rounded-lg bg-[#1a1a1a] border border-white/[0.08] text-[10px] font-semibold text-text-primary whitespace-nowrap opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-150 z-10 shadow-xl pointer-events-none">
                                {platformLabel}{postNum > 0 ? ` #${postNum}` : " slot"}
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  </>
                );
              })()}

              <div className="flex items-center gap-4 mt-4 text-[10px] font-semibold text-text-tertiary">
                <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded bg-facebook" /> Facebook</span>
                <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded bg-instagram" /> Instagram</span>
                <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded bg-tiktok" /> TikTok</span>
                <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded bg-[#1a1a1a]" /> None</span>
              </div>
            </BentoCard>
          </div>

          {/* ROW 4: Platform Detail Cards */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Users className="w-4 h-4 text-text-tertiary" />
              <h2 className="font-[family-name:var(--font-space-grotesk)] text-lg font-bold tracking-tight">
                Platform Details
              </h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {fbData && (
                <PlatformCard
                  platform="facebook"
                  score={fbScore}
                  username={selectedClient?.facebook}
                  stats={[
                    { label: "Posts", value: fbData.content_breakdown?.posts ?? 0 },
                    { label: "Videos", value: fbData.content_breakdown?.videos ?? 0 },
                    { label: "Total", value: fbData.total_posts_delivered ?? 0 },
                  ]}
                />
              )}

              {igData && (
                <PlatformCard
                  platform="instagram"
                  score={igScore}
                  username={selectedClient?.instagram}
                  stats={[
                    { label: "Carousel", value: igData.content_types?.carousel ?? 0 },
                    { label: "Images", value: igData.content_types?.image ?? 0 },
                    { label: "Videos", value: igData.content_types?.video ?? 0 },
                  ]}
                >
                  <div className="mt-4 bg-[#0a0a0a] rounded-2xl p-4">
                    <div className="text-[10px] font-bold uppercase tracking-wider text-text-tertiary mb-2">Collaborations</div>
                    <div className="grid grid-cols-3 gap-2 text-center">
                      <div>
                        <div className="font-[family-name:var(--font-space-grotesk)] text-xl font-bold text-accent-purple">
                          {igData.collaboration_stats?.collaborative_posts ?? 0}
                        </div>
                        <div className="text-[9px] text-text-tertiary mt-0.5">Collabs</div>
                      </div>
                      <div>
                        <div className="font-[family-name:var(--font-space-grotesk)] text-xl font-bold">
                          {igData.collaboration_stats?.solo_posts ?? 0}
                        </div>
                        <div className="text-[9px] text-text-tertiary mt-0.5">Solo</div>
                      </div>
                      <div>
                        <div className="font-[family-name:var(--font-space-grotesk)] text-xl font-bold text-accent-lime">
                          {igData.collaboration_stats?.collaboration_rate ?? "0%"}
                        </div>
                        <div className="text-[9px] text-text-tertiary mt-0.5">Rate</div>
                      </div>
                    </div>
                  </div>
                </PlatformCard>
              )}

              {ttData && (
                <PlatformCard
                  platform="tiktok"
                  score={ttScore}
                  username={selectedClient?.tiktok}
                  stats={[
                    { label: "Videos", value: ttData.content_breakdown?.videos ?? 0 },
                    { label: "Images", value: ttData.content_breakdown?.images ?? 0 },
                    { label: "Total", value: ttData.total_videos_delivered ?? 0 },
                  ]}
                />
              )}
            </div>
          </div>

          {/* ROW 5: AI Analysis */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <span className="text-base">&#x1F916;</span>
              <h2 className="font-[family-name:var(--font-space-grotesk)] text-lg font-bold tracking-tight">
                AI Analysis
              </h2>
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
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
