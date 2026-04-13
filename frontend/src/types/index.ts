export interface Client {
  id: number;
  name: string;
  facebook: string | null;
  instagram: string | null;
  tiktok: string | null;
  contract?: string | null;
}

export interface ClientsResponse {
  total: number;
  clients: Client[];
}

export interface ComplianceAnalysis {
  compliance_status: string;
  compliance_score: number;
  analysis: string;
  deliverables_met: string[];
  deliverables_missing: string[];
  recommendations: string[];
  post_frequency?: {
    required: string;
    delivered: string;
    status: string;
  };
  content_quality?: {
    assessment: string;
    score: number;
  };
  content_breakdown?: Record<string, number | string>;
  collaborations?: {
    collaborative_posts: number;
    solo_posts: number;
    collaboration_rate: string;
    status: string;
  };
}

export interface FacebookComplianceData {
  platform: "facebook";
  username: string;
  client_name: string;
  date_range: { start: string; end: string };
  total_posts_delivered: number;
  content_breakdown: {
    posts: number;
    videos: number;
    total: number;
    note: string;
  };
  contract_preview: string;
  compliance_analysis: ComplianceAnalysis;
}

export interface InstagramComplianceData {
  platform: "instagram";
  username: string;
  client_name: string;
  date_range: { start: string; end: string };
  total_posts_delivered: number;
  content_types: {
    carousel: number;
    image: number;
    video: number;
    total: number;
    note: string;
  };
  collaboration_stats: {
    collaborative_posts: number;
    solo_posts: number;
    total: number;
    collaboration_rate: string;
    note: string;
  };
  contract_preview: string;
  compliance_analysis: ComplianceAnalysis;
}

export interface TikTokComplianceData {
  platform: "tiktok";
  username: string;
  client_name: string;
  date_range: { start: string; end: string };
  total_videos_delivered: number;
  content_breakdown: {
    videos: number;
    images: number;
    total: number;
    note: string;
  };
  contract_preview: string;
  compliance_analysis: ComplianceAnalysis;
}

export type PlatformData =
  | FacebookComplianceData
  | InstagramComplianceData
  | TikTokComplianceData;
