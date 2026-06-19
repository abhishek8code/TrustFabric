import React, { useEffect, useState } from "react";
import { api } from "../api/client";
import { TrustMeter } from "../components/TrustMeter";

export const TrustPassportPage: React.FC = () => {
  const [passport, setPassport] = useState<any>(null);
  const [errorMsg, setErrorMsg] = useState<string>("");

  useEffect(() => {
    api.get("/trust-passport/me")
      .then((response) => {
        setPassport(response.data);
      })
      .catch((err) => {
        setErrorMsg("Failed to retrieve passport. Is the server running?");
      });
  }, []);

  if (errorMsg) return <div className="p-8 text-rose-400 text-center">{errorMsg}</div>;
  if (!passport) return <div className="p-8 text-slate-400 text-center">Loading your Security Passport...</div>;

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="rounded-3xl border border-slate-800 bg-slate-950/70 p-8 backdrop-blur-md relative overflow-hidden text-center">
        <div className="absolute top-0 left-0 w-full h-1.5 bg-gradient-to-r from-sky-500 to-indigo-500" />
        
        <h1 className="text-3xl font-extrabold text-white tracking-tight">Your Security Trust Passport</h1>
        <p className="text-sm text-slate-400 mt-2">
          Your dynamic bank trust status, verified cryptographically.
        </p>
        
        <div className="mt-8 flex justify-center">
          <TrustMeter score={passport.trust_score} level={passport.trust_level} size={200} />
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Dynamic Explanations */}
        <div className="rounded-3xl border border-slate-800 bg-slate-950/70 p-6 backdrop-blur-md">
          <h3 className="text-slate-400 text-xs font-bold uppercase tracking-wider mb-4">
            Why is my score {Math.round(passport.trust_score)}?
          </h3>
          <ul className="space-y-3.5">
            {passport.explanation?.map((item: string, i: number) => (
              <li key={i} className="flex items-start gap-3 text-sm">
                <span className={`inline-block mt-0.5 rounded-full px-1.5 py-0.5 text-[10px] font-bold ${
                  item.includes("✓") ? "bg-emerald-950 text-emerald-400 border border-emerald-900/50" : "bg-amber-950 text-amber-400 border border-amber-900/50"
                }`}>
                  {item.includes("✓") ? "✓" : "⚠"}
                </span>
                <span className="text-slate-300 leading-normal">{item}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Security Event History */}
        <div className="rounded-3xl border border-slate-800 bg-slate-950/70 p-6 backdrop-blur-md">
          <h3 className="text-slate-400 text-xs font-bold uppercase tracking-wider mb-4">
            Recent Security Events
          </h3>
          <div className="space-y-4">
            {passport.recent_events?.map((ev: any, i: number) => (
              <div key={i} className="flex justify-between items-center py-2.5 border-b border-slate-900 text-sm">
                <span className="text-slate-300 pr-4">{ev.description}</span>
                <span className="text-slate-500 text-xs shrink-0">{ev.time}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <p className="text-slate-500 text-center text-xs">
        TrustFabric does not store raw biometrics. All security tokens are signed using local cryptography.
      </p>
    </div>
  );
};
