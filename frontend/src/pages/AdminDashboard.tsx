import React, { useEffect, useState } from "react";
import { api } from "../api/client";
import { AlertFeed } from "../components/AlertFeed";

export const AdminDashboard: React.FC = () => {
  const [alerts, setAlerts] = useState<Array<{ id: string; severity: string; message: string }>>([]);
  const [refreshKey, setRefreshKey] = useState<number>(0);
  
  // KYC application inputs
  const [fullName, setFullName] = useState("Priya Sharma");
  const [dob, setDob] = useState("1994-05-12");
  const [mobile, setMobile] = useState("9876");
  const [pincode, setPincode] = useState("382355");
  const [emailDomain, setEmailDomain] = useState("gmail.com");

  const [onboardingResult, setOnboardingResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.get("/admin/alerts").then((response) => setAlerts(response.data.alerts));
  }, [refreshKey]);

  const triggerOnboarding = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setOnboardingResult(null);

    try {
      const response = await api.post("/onboarding/check", {
        application_id: `APP-${Math.floor(10000 + Math.random() * 90000)}`,
        full_name: fullName,
        aadhaar_hash: "mock-aadhaar-hash-hash",
        pan_hash: "mock-pan-hash-hash",
        dob: dob,
        mobile_last4: mobile,
        pincode: pincode,
        email_domain: emailDomain,
      });

      setOnboardingResult(response.data);
      // Trigger alerts reload
      setRefreshKey(prev => prev + 1);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid gap-6 md:grid-cols-[1.2fr,1fr]">
      {/* Dynamic Alerts Feed */}
      <div className="space-y-6">
        <div className="flex justify-between items-center bg-slate-950/40 p-4 border border-slate-900 rounded-3xl">
          <div>
            <h2 className="text-xl font-extrabold text-white tracking-tight">SOC Dashboard</h2>
            <p className="text-xs text-slate-500">Security Operations Center - Real-Time Alert Feed</p>
          </div>
          <button
            onClick={() => setRefreshKey(prev => prev + 1)}
            className="rounded-xl border border-slate-800 bg-slate-950/70 hover:bg-slate-900 text-xs px-3 py-2 text-slate-300 font-semibold transition"
          >
            Refresh Feed
          </button>
        </div>

        <div className="glass rounded-3xl p-6 relative overflow-hidden">
          <div className="absolute top-0 left-0 w-full h-1.5 bg-gradient-to-r from-red-500 to-rose-500" />
          
          <h3 className="text-slate-300 font-bold uppercase tracking-wider text-xs mb-4">Analyst Threat Alerts</h3>
          <div className="space-y-3.5 max-h-[500px] overflow-y-auto pr-2">
            {alerts.map((alert) => (
              <div key={alert.id} className="rounded-2xl border border-slate-900 bg-slate-950/60 p-4 flex gap-4 items-start transition hover:border-slate-800">
                <span className={`px-2 py-0.5 rounded text-[10px] uppercase font-bold shrink-0 mt-0.5 ${
                  alert.severity === "high"
                    ? "bg-rose-950/50 text-rose-400 border border-rose-900/50"
                    : "bg-amber-950/50 text-amber-400 border border-amber-900/50"
                }`}>
                  {alert.severity}
                </span>
                <div>
                  <div className="flex items-center gap-2 text-[10px] text-slate-500 font-mono">
                    <span>ID: {alert.id}</span>
                  </div>
                  <p className="mt-1 text-sm text-slate-200 leading-normal">{alert.message}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* KYC Onboarding recycling simulator */}
      <div className="space-y-6">
        <div className="rounded-3xl border border-slate-800 bg-slate-950/70 p-6 backdrop-blur-md relative overflow-hidden">
          <div className="absolute top-0 left-0 w-full h-1.5 bg-gradient-to-r from-indigo-500 to-sky-500" />
          
          <h2 className="text-xl font-extrabold text-white tracking-tight mb-1">KYC Onboarding Checker</h2>
          <p className="text-xs text-slate-400 mb-6">Simulate new onboarding applications. Recycling detection checks embeddings similarity.</p>

          <form onSubmit={triggerOnboarding} className="space-y-4 text-xs">
            <div>
              <label className="block text-slate-400 font-bold uppercase tracking-wider mb-1">Full Name</label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full rounded-xl border border-slate-800 bg-slate-900 px-3 py-2 text-white outline-none focus:border-indigo-500"
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-slate-400 font-bold uppercase tracking-wider mb-1">Date of Birth</label>
                <input
                  type="date"
                  value={dob}
                  onChange={(e) => setDob(e.target.value)}
                  className="w-full rounded-xl border border-slate-800 bg-slate-900 px-3 py-2 text-white outline-none focus:border-indigo-500"
                  required
                />
              </div>
              <div>
                <label className="block text-slate-400 font-bold uppercase tracking-wider mb-1">Mobile (Last 4 digits)</label>
                <input
                  type="text"
                  value={mobile}
                  onChange={(e) => setMobile(e.target.value)}
                  maxLength={4}
                  className="w-full rounded-xl border border-slate-800 bg-slate-900 px-3 py-2 text-white outline-none focus:border-indigo-500 font-mono"
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-slate-400 font-bold uppercase tracking-wider mb-1">Pincode</label>
                <input
                  type="text"
                  value={pincode}
                  onChange={(e) => setPincode(e.target.value)}
                  maxLength={6}
                  className="w-full rounded-xl border border-slate-800 bg-slate-900 px-3 py-2 text-white outline-none focus:border-indigo-500 font-mono"
                  required
                />
              </div>
              <div>
                <label className="block text-slate-400 font-bold uppercase tracking-wider mb-1">Email Domain</label>
                <select
                  value={emailDomain}
                  onChange={(e) => setEmailDomain(e.target.value)}
                  className="w-full rounded-xl border border-slate-800 bg-slate-900 px-3 py-2 text-white outline-none focus:border-indigo-500"
                >
                  <option value="gmail.com">gmail.com</option>
                  <option value="yahoo.com">yahoo.com</option>
                  <option value="bob.co.in">bob.co.in</option>
                  <option value="tempmail.com">tempmail.com</option>
                </select>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-xl bg-gradient-to-r from-indigo-500 to-sky-500 hover:from-indigo-400 hover:to-sky-400 py-3 font-bold text-white shadow-md transition active:scale-[0.98]"
            >
              {loading ? "Checking Identity..." : "Submit KYC Application"}
            </button>
          </form>

          {onboardingResult && (
            <div className={`mt-5 p-4 rounded-2xl border text-xs leading-normal animate-fadeIn ${
              onboardingResult.risk_level === "CLEAR"
                ? "bg-emerald-950/20 border-emerald-800/40 text-emerald-300"
                : onboardingResult.risk_level === "REVIEW"
                ? "bg-amber-950/20 border-amber-800/40 text-amber-300"
                : "bg-rose-950/20 border-rose-800/40 text-rose-300"
            }`}>
              <div className="flex justify-between font-bold text-[10px] uppercase tracking-wider mb-2">
                <span>KYC Verification Status</span>
                <span>{onboardingResult.risk_level}</span>
              </div>
              <p className="font-semibold text-slate-100 mb-1">Cosine Similarity Match: {Math.round(onboardingResult.max_similarity_score * 100)}%</p>
              <p>{onboardingResult.explanation}</p>
              {onboardingResult.closest_match_id && (
                <p className="mt-2 text-slate-400 font-mono">Closest Match ID: {onboardingResult.closest_match_id}</p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
