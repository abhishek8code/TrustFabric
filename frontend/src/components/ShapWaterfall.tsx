import React from "react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export type ShapFeature = {
  feature: string;
  value: number;
  shap_impact: number;
};

export const ShapWaterfall: React.FC<{ features: ShapFeature[] }> = ({ features }) => {
  const data = [...features].sort((a, b) => Math.abs(b.shap_impact) - Math.abs(a.shap_impact));

  return (
    <div className="glass rounded-2xl p-4">
      <h3 className="text-slate-200 font-semibold mb-4">Why this transaction was flagged</h3>
      <ResponsiveContainer width="100%" height={320}>
        <BarChart data={data} layout="vertical" margin={{ left: 20, right: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
          <XAxis type="number" stroke="#94a3b8" />
          <YAxis type="category" dataKey="feature" stroke="#94a3b8" width={120} />
          <Tooltip
            contentStyle={{ background: "#0f172a", border: "1px solid #334155" }}
            formatter={(_, __, payload: any) => [payload?.payload?.value, "Raw value"]}
          />
          <Bar dataKey="shap_impact" fill="#f97316" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
