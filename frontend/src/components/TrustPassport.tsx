import React from "react";

export const TrustPassport: React.FC<{ trust_score: number; trust_level: string; explanation: string[] }> = ({ trust_score, trust_level, explanation }) => (
  <div className="glass rounded-2xl p-5">
    <div className="flex items-center justify-between gap-4">
      <div>
        <p className="text-xs uppercase tracking-[0.3em] text-sky-300">Trust Passport</p>
        <h3 className="mt-2 text-2xl font-semibold text-white">Your bank trust summary</h3>
      </div>
      <div className="rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-right">
        <div className="text-3xl font-bold text-white">{Math.round(trust_score)}</div>
        <div className="text-xs uppercase tracking-[0.2em] text-slate-400">{trust_level}</div>
      </div>
    </div>
    <ul className="mt-5 space-y-3 text-sm text-slate-300">
      {explanation.map((item) => (
        <li key={item} className="flex gap-3">
          <span className={item.includes("✓") ? "text-emerald-400" : "text-amber-400"}>{item.includes("✓") ? "✓" : "⚠"}</span>
          <span>{item}</span>
        </li>
      ))}
    </ul>
  </div>
);
