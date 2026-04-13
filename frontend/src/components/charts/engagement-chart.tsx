"use client";

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

interface EngagementChartProps {
  data: Array<{
    date: string;
    facebook: number;
    instagram: number;
    tiktok: number;
  }>;
}

function CustomTooltip({ active, payload, label }: { active?: boolean; payload?: Array<{ color: string; name: string; value: number }>; label?: string }) {
  if (!active || !payload) return null;
  return (
    <div className="bg-bg-elevated border border-border rounded-lg p-3 shadow-xl">
      <p className="text-xs font-semibold text-text-primary mb-2">{label}</p>
      {payload.map((entry, i) => (
        <p key={i} className="text-xs flex items-center gap-2">
          <span
            className="w-2 h-2 rounded-full inline-block"
            style={{ backgroundColor: entry.color }}
          />
          <span className="text-text-secondary capitalize">{entry.name}:</span>
          <span className="font-mono font-semibold">{entry.value}</span>
        </p>
      ))}
    </div>
  );
}

export function EngagementChart({ data }: EngagementChartProps) {
  return (
    <div className="bg-bg-card rounded-xl border border-border p-5">
      <h3 className="text-sm font-bold mb-4">Engagement Over Time</h3>
      <ResponsiveContainer width="100%" height={280}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="fbGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#1877f2" stopOpacity={0.3} />
              <stop offset="100%" stopColor="#1877f2" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="igGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#e6683c" stopOpacity={0.3} />
              <stop offset="100%" stopColor="#e6683c" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="ttGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#00f2ea" stopOpacity={0.3} />
              <stop offset="100%" stopColor="#00f2ea" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e1e1e" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 11, fill: "#8b9299" }}
            axisLine={{ stroke: "#1e1e1e" }}
            tickLine={false}
          />
          <YAxis
            tick={{ fontSize: 11, fill: "#8b9299" }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            iconType="circle"
            iconSize={8}
            wrapperStyle={{ fontSize: 11, color: "#8b9299" }}
          />
          <Area
            type="monotone"
            dataKey="facebook"
            stroke="#1877f2"
            fill="url(#fbGradient)"
            strokeWidth={2}
          />
          <Area
            type="monotone"
            dataKey="instagram"
            stroke="#e6683c"
            fill="url(#igGradient)"
            strokeWidth={2}
          />
          <Area
            type="monotone"
            dataKey="tiktok"
            stroke="#00f2ea"
            fill="url(#ttGradient)"
            strokeWidth={2}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
