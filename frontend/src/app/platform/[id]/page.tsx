"use client";

import { useParams } from "next/navigation";
import { StatCard } from "@/components/ui/stat-card";
import { ComplianceAnalysisPanel } from "@/components/ui/compliance-analysis-panel";
import {
  PlatformScoreRing,
  PlatformChart,
  PlatformGrowthInsights,
} from "@/components/dashboard/client-widgets";
import {
  mockEngagementData,
  growthInsights,
  clientSocialLinks,
  contentPerformance,
} from "@/lib/mock-data";
import { useDashboard } from "@/components/dashboard-context";
import { parseContractTargets } from "@/lib/contract-targets";
import { FacebookIcon, InstagramIcon, TikTokIcon } from "@/components/icons/social-icons";
import { Loader2 } from "lucide-react";

const platformColors: Record<string, string> = {
  facebook: "var(--color-facebook)",
  instagram: "var(--color-instagram)",
  tiktok: "var(--color-tiktok)",
};

const platformIcons: Record<string, typeof FacebookIcon> = {
  facebook: FacebookIcon,
  instagram: InstagramIcon,
  tiktok: TikTokIcon,
};

const platformUrls: Record<string, string> = {
  facebook: "https://facebook.com",
  instagram: "https://instagram.com",
  tiktok: "https://tiktok.com",
};

export default function PlatformPage() {
  const { id } = useParams<{ id: string }>();
  const { selectedClient, data, loading } = useDashboard();

  const platformData = id === "facebook" ? data.facebook : id === "instagram" ? data.instagram : id === "tiktok" ? data.tiktok : null;

  if (loading && !platformData) {
    return (
      <div className="flex items-center justify-center h-64 gap-3 text-text-secondary">
        <Loader2 className="w-5 h-5 animate-spin" />
        <span className="text-sm">Loading {id} data…</span>
      </div>
    );
  }

  if (!platformData || !id) {
    return (
      <div className="flex items-center justify-center h-64 text-text-secondary text-sm">
        No data available for this platform.
      </div>
    );
  }

  const color = platformColors[id] ?? "var(--color-accent)";
  const Icon = platformIcons[id] ?? FacebookIcon;
  const score = platformData.compliance_analysis.compliance_score;
  const breakdown = platformData.content_breakdown;
  const clientName = selectedClient?.name ?? "—";
  const socialLinks = (clientSocialLinks[clientName] ?? []).filter(
    (l) => l.platform === id
  );
  const insights = growthInsights[id] ?? [];
  const perfKey = id as keyof typeof contentPerformance.bestPostingTimes;
  const targets = parseContractTargets(selectedClient?.contract);
  const target = targets[id as keyof typeof targets] ?? 0;

  return (
    <div className="space-y-8 pb-20 md:pb-6">
      {/* Platform header */}
      <div className="flex items-center gap-4">
        <div
          className="w-12 h-12 rounded-xl flex items-center justify-center"
          style={{ backgroundColor: `color-mix(in srgb, ${color} 12%, transparent)` }}
        >
          <Icon className="w-6 h-6" style={{ color }} />
        </div>
        <div>
          <h1 className="text-xl font-bold capitalize">{id}</h1>
          <p className="text-sm text-text-secondary">
            @{platformData.username} — {platformData.date_range.start} to {platformData.date_range.end}
          </p>
        </div>
        <a
          href={`${platformUrls[id]}/${platformData.username}`}
          target="_blank"
          rel="noopener noreferrer"
          className="ml-auto text-xs font-medium px-3 py-1.5 rounded-lg border border-border hover:border-border-hover transition-colors"
          style={{ color }}
        >
          Visit Profile →
        </a>
      </div>

      {/* Score + Stats — current / target */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-5 items-start">
        <PlatformScoreRing
          score={score}
          color={color}
          status={platformData.compliance_analysis.compliance_status}
        />
        <div className="md:col-span-3 grid grid-cols-2 md:grid-cols-3 gap-4">
          <StatCard
            label="Delivered / Target"
            value={`${platformData.total_posts_delivered} / ${target}`}
            sublabel={
              target > 0
                ? platformData.total_posts_delivered >= target
                  ? "Target met"
                  : `${target - platformData.total_posts_delivered} short of target`
                : undefined
            }
            trend={
              target > 0
                ? platformData.total_posts_delivered >= target
                  ? "up"
                  : "down"
                : undefined
            }
            accentColor={color}
            delay={0}
          />
          {breakdown.posts !== undefined && (
            <StatCard label="Posts" value={breakdown.posts} delay={0.05} />
          )}
          {breakdown.videos !== undefined && (
            <StatCard label="Videos" value={breakdown.videos} delay={0.1} />
          )}
          {breakdown.carousel !== undefined && (
            <StatCard label="Carousels" value={breakdown.carousel} delay={0.05} />
          )}
          {breakdown.image !== undefined && (
            <StatCard label="Images" value={breakdown.image} delay={0.1} />
          )}
          {breakdown.video !== undefined && (
            <StatCard label="Reels / Videos" value={breakdown.video} delay={0.15} />
          )}
          {breakdown.images !== undefined && (
            <StatCard label="Image Posts" value={breakdown.images} delay={0.15} />
          )}
          {platformData.collaboration_stats && (
            <>
              <StatCard
                label="Collaborations"
                value={platformData.collaboration_stats.collaborative}
                sublabel={`${platformData.collaboration_stats.collaboration_rate}% collab rate`}
                delay={0.2}
              />
              <StatCard
                label="Solo Posts"
                value={platformData.collaboration_stats.solo}
                delay={0.25}
              />
            </>
          )}
        </div>
      </div>

      {/* Growth Insights + Social Links + Quick Metrics */}
      <PlatformGrowthInsights
        insights={insights}
        platform={id.charAt(0).toUpperCase() + id.slice(1)}
        platformColor={color}
        socialLinks={socialLinks}
        clientName={clientName}
        engagementRate={contentPerformance.engagementRates[perfKey]}
        bestTime={contentPerformance.bestPostingTimes[perfKey]}
        topContent={contentPerformance.topContentTypes[perfKey]}
      />

      {/* Chart */}
      <PlatformChart engagementData={mockEngagementData} />

      {/* Analysis */}
      <ComplianceAnalysisPanel
        analysis={platformData.compliance_analysis}
        platform={id}
      />
    </div>
  );
}
