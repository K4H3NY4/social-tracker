"use client";

import dynamic from "next/dynamic";
import { MetricRing } from "@/components/ui/metric-ring";
import { SocialLinksGateway } from "@/components/ui/social-links-gateway";
import { GrowthInsightsPanel, QuickInsight } from "@/components/ui/growth-insights";
import type { SocialLink, MarketingInsight } from "@/lib/mock-data";
import { Clock, Target, TrendingUp } from "lucide-react";

const EngagementChart = dynamic(
  () =>
    import("@/components/charts/engagement-chart").then(
      (mod) => mod.EngagementChart
    ),
  { ssr: false }
);

const PostFrequencyChart = dynamic(
  () =>
    import("@/components/charts/post-frequency-chart").then(
      (mod) => mod.PostFrequencyChart
    ),
  { ssr: false }
);

interface DashboardChartsProps {
  engagementData: Array<{
    date: string;
    facebook: number;
    instagram: number;
    tiktok: number;
  }>;
  postFrequencyData: Array<{
    week: string;
    facebook: number;
    instagram: number;
    tiktok: number;
  }>;
}

export function DashboardCharts({
  engagementData,
  postFrequencyData,
}: DashboardChartsProps) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
      <EngagementChart data={engagementData} />
      <PostFrequencyChart data={postFrequencyData} />
    </div>
  );
}

interface PlatformChartProps {
  engagementData: Array<{
    date: string;
    facebook: number;
    instagram: number;
    tiktok: number;
  }>;
}

export function PlatformChart({ engagementData }: PlatformChartProps) {
  return <EngagementChart data={engagementData} />;
}

interface ComplianceRingsProps {
  overall: number;
  facebook: number;
  instagram: number;
  tiktok: number;
}

export function ComplianceRings({
  overall,
  facebook,
  instagram,
  tiktok,
}: ComplianceRingsProps) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-5">
      <div className="col-span-2 md:col-span-1 flex justify-center">
        <MetricRing
          value={overall}
          size={140}
          strokeWidth={10}
          color="var(--color-accent)"
          label="Overall Score"
          sublabel="Across all platforms"
        />
      </div>
      <div className="flex justify-center">
        <MetricRing
          value={facebook}
          size={110}
          strokeWidth={7}
          color="var(--color-facebook)"
          label="Facebook"
        />
      </div>
      <div className="flex justify-center">
        <MetricRing
          value={instagram}
          size={110}
          strokeWidth={7}
          color="var(--color-instagram)"
          label="Instagram"
        />
      </div>
      <div className="flex justify-center">
        <MetricRing
          value={tiktok}
          size={110}
          strokeWidth={7}
          color="var(--color-tiktok)"
          label="TikTok"
        />
      </div>
    </div>
  );
}

interface PlatformScoreRingProps {
  score: number;
  color: string;
  status: string;
}

export function PlatformScoreRing({ score, color, status }: PlatformScoreRingProps) {
  return (
    <div className="flex justify-center md:justify-start">
      <MetricRing
        value={score}
        size={160}
        strokeWidth={12}
        color={color}
        label="Compliance Score"
        sublabel={status.replace(/_/g, " ")}
      />
    </div>
  );
}

interface DashboardAnimatedSectionsProps {
  socialLinks: SocialLink[];
  clientName: string;
  growthInsights: Record<string, MarketingInsight[]>;
  contentPerformance: {
    bestPostingTimes: Record<string, { day: string; time: string; timezone: string }>;
    topContentTypes: Record<string, { type: string; avgEngagement: number }>;
    engagementRates: Record<string, { current: number; previous: number; change: number }>;
  };
}

export function DashboardAnimatedSections({
  socialLinks,
  clientName,
  growthInsights,
  contentPerformance,
}: DashboardAnimatedSectionsProps) {
  return (
    <div className="space-y-5">
      {/* Social Links Gateway */}
      <SocialLinksGateway links={socialLinks} clientName={clientName} />

      {/* Performance Quick Metrics */}
      <div className="bg-bg-card rounded-xl border border-border p-5">
        <h3 className="text-sm font-bold text-text-secondary uppercase tracking-wider mb-4">
          Performance Snapshot
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
          <QuickInsight
            icon={Clock}
            label="Best FB Time"
            value={contentPerformance.bestPostingTimes.facebook.time}
            sublabel={contentPerformance.bestPostingTimes.facebook.day}
            color="var(--color-facebook)"
          />
          <QuickInsight
            icon={Clock}
            label="Best IG Time"
            value={contentPerformance.bestPostingTimes.instagram.time}
            sublabel={contentPerformance.bestPostingTimes.instagram.day}
            color="var(--color-instagram)"
          />
          <QuickInsight
            icon={Clock}
            label="Best TT Time"
            value={contentPerformance.bestPostingTimes.tiktok.time}
            sublabel={contentPerformance.bestPostingTimes.tiktok.day}
            color="var(--color-tiktok)"
          />
          <QuickInsight
            icon={Target}
            label="Top FB Content"
            value={contentPerformance.topContentTypes.facebook.type}
            sublabel={`${contentPerformance.topContentTypes.facebook.avgEngagement}% engagement`}
            color="var(--color-facebook)"
          />
          <QuickInsight
            icon={Target}
            label="Top IG Content"
            value={contentPerformance.topContentTypes.instagram.type}
            sublabel={`${contentPerformance.topContentTypes.instagram.avgEngagement}% engagement`}
            color="var(--color-instagram)"
          />
          <QuickInsight
            icon={TrendingUp}
            label="TT Engagement"
            value={`${contentPerformance.engagementRates.tiktok.current}%`}
            sublabel={`${contentPerformance.engagementRates.tiktok.change > 0 ? "+" : ""}${contentPerformance.engagementRates.tiktok.change}% MoM`}
            color="var(--color-tiktok)"
          />
        </div>
      </div>

      {/* Growth Insights per platform */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <GrowthInsightsPanel
          insights={growthInsights.facebook}
          platform="Facebook"
          platformColor="var(--color-facebook)"
        />
        <GrowthInsightsPanel
          insights={growthInsights.instagram}
          platform="Instagram"
          platformColor="var(--color-instagram)"
        />
        <GrowthInsightsPanel
          insights={growthInsights.tiktok}
          platform="TikTok"
          platformColor="var(--color-tiktok)"
        />
      </div>
    </div>
  );
}

interface PlatformGrowthInsightsProps {
  insights: MarketingInsight[];
  platform: string;
  platformColor: string;
  socialLinks?: SocialLink[];
  clientName?: string;
  engagementRate?: { current: number; previous: number; change: number };
  bestTime?: { day: string; time: string; timezone: string };
  topContent?: { type: string; avgEngagement: number };
}

export function PlatformGrowthInsights({
  insights,
  platform,
  platformColor,
  socialLinks,
  clientName,
  engagementRate,
  bestTime,
  topContent,
}: PlatformGrowthInsightsProps) {
  return (
    <div className="space-y-5">
      {/* Social link for this platform */}
      {socialLinks && clientName && (
        <SocialLinksGateway links={socialLinks} clientName={clientName} />
      )}

      {/* Quick metrics row */}
      {(engagementRate || bestTime || topContent) && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {bestTime && (
            <QuickInsight
              icon={Clock}
              label="Best Posting Time"
              value={bestTime.time}
              sublabel={`${bestTime.day} (${bestTime.timezone})`}
              color={platformColor}
            />
          )}
          {topContent && (
            <QuickInsight
              icon={Target}
              label="Top Content Type"
              value={topContent.type}
              sublabel={`${topContent.avgEngagement}% avg engagement`}
              color={platformColor}
            />
          )}
          {engagementRate && (
            <QuickInsight
              icon={TrendingUp}
              label="Engagement Rate"
              value={`${engagementRate.current}%`}
              sublabel={`${engagementRate.change > 0 ? "+" : ""}${engagementRate.change}% vs last month`}
              color={platformColor}
            />
          )}
        </div>
      )}

      {/* Growth insights */}
      <GrowthInsightsPanel
        insights={insights}
        platform={platform}
        platformColor={platformColor}
      />
    </div>
  );
}
