"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

interface PostFrequencyChartProps {
  data: Array<{
    week: string;
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

export function PostFrequencyChart({ data }: PostFrequencyChartProps) {
  return (
    <div className="bg-bg-card rounded-xl border border-border p-5">
      <h3 className="text-sm font-bold mb-4">Weekly Post Frequency</h3>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={data} barCategoryGap="20%">
          <CartesianGrid strokeDasharray="3 3" stroke="#1e1e1e" />
          <XAxis
            dataKey="week"
            tick={{ fontSize: 11, fill: "#8b9299" }}
            axisLine={{ stroke: "#1e1e1e" }}
            tickLine={false}
          />
          <YAxis
            tick={{ fontSize: 11, fill: "#8b9299" }}
            axisLine={false}
            tickLine={false}
            allowDecimals={false}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            iconType="circle"
            iconSize={8}
            wrapperStyle={{ fontSize: 11, color: "#8b9299" }}
          />
          <Bar dataKey="facebook" fill="#1877f2" radius={[4, 4, 0, 0]} />
          <Bar dataKey="instagram" fill="#e6683c" radius={[4, 4, 0, 0]} />
          <Bar dataKey="tiktok" fill="#00f2ea" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
