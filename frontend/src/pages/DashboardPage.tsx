import React from "react";
import { TrustMeter } from "../components/TrustMeter";
import { useTrustStore } from "../store/trustStore";

export const DashboardPage: React.FC = () => {
  const score = useTrustStore((state) => state.score);
  const level = useTrustStore((state) => state.level);
  return (
    <div className="grid gap-6 md:grid-cols-[320px,1fr]">
      <div className="glass rounded-3xl p-6">
        <TrustMeter score={score} level={level} size={220} />
      </div>
      <div className="glass rounded-3xl p-6">
        <h2 className="text-2xl font-semibold text-white">Session overview</h2>
        <p className="mt-3 text-sm text-slate-300">This dashboard is the customer-facing trust view. It can anchor login, transfers, and step-up flows.</p>
      </div>
    </div>
  );
};
