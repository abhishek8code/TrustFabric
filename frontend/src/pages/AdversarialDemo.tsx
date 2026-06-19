import React, { useState } from "react";
import { api } from "../api/client";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis, CartesianGrid } from "recharts";

type AttackType = "SPOOFED_BIOMETRICS" | "BOILING_FROG" | "GRAPH_EVASION";

export const AdversarialDemo: React.FC = () => {
  const [selectedAttack, setSelectedAttack] = useState<AttackType>("BOILING_FROG");
  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<any>(null);
  const [errorMsg, setErrorMsg] = useState<string>("");

  const runSimulation = async () => {
    setLoading(true);
    setErrorMsg("");
    setResult(null);

    try {
      const response = await api.get(`/adversarial/simulate?attack=${selectedAttack}`);
      setResult(response.data.result);
    } catch (err: any) {
      setErrorMsg("Failed to connect to backend simulation service.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid gap-6 md:grid-cols-[300px,1fr]">
      {/* Simulation Controller */}
      <div className="rounded-3xl border border-slate-800 bg-slate-950/70 p-6 backdrop-blur-md relative overflow-hidden h-fit">
        <div className="absolute top-0 left-0 w-full h-1.5 bg-gradient-to-r from-rose-500 to-red-500" />
        
        <h2 className="text-xl font-extrabold text-white tracking-tight mb-2">Red-Team Simulator</h2>
        <p className="text-xs text-slate-400 mb-6">Test the trust layer against advanced adversarial evasion techniques.</p>

        <div className="space-y-4">
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Select Attack Scenario</label>
            <div className="space-y-2">
              {[
                { id: "SPOOFED_BIOMETRICS", label: "Spoofed Biometrics", desc: "Adversary mimics population-average keystrokes" },
                { id: "BOILING_FROG", label: "Boiling Frog ATO", desc: "Gradual takeover changing rhythm slowly over 15 sessions" },
                { id: "GRAPH_EVASION", label: "Graph Evasion", desc: "Routing funds through clean hops to dodge Louvain community detection" }
              ].map((atk) => (
                <button
                  key={atk.id}
                  type="button"
                  onClick={() => {
                    setSelectedAttack(atk.id as AttackType);
                    setResult(null);
                    setErrorMsg("");
                  }}
                  className={`w-full text-left p-3 rounded-xl border text-sm transition ${
                    selectedAttack === atk.id
                      ? "bg-rose-950/30 border-rose-500/50 text-white"
                      : "bg-slate-900/50 border-slate-800 text-slate-300 hover:bg-slate-900"
                  }`}
                >
                  <p className="font-semibold">{atk.label}</p>
                  <p className="text-[11px] text-slate-500 mt-0.5">{atk.desc}</p>
                </button>
              ))}
            </div>
          </div>

          <button
            onClick={runSimulation}
            disabled={loading}
            className="w-full rounded-xl bg-gradient-to-r from-rose-500 to-red-500 hover:from-rose-400 hover:to-red-400 py-3 font-bold text-white shadow-md transition active:scale-[0.98]"
          >
            {loading ? "Running Red-Team..." : "Launch Simulation"}
          </button>
        </div>

        {errorMsg && (
          <div className="mt-4 p-3 rounded-xl bg-rose-950/50 border border-rose-900/50 text-xs text-rose-400 text-center">
            {errorMsg}
          </div>
        )}
      </div>

      {/* Result Workspace */}
      <div className="space-y-6">
        {result ? (
          <div className="rounded-3xl border border-slate-800 bg-slate-950/70 p-6 backdrop-blur-md relative overflow-hidden">
            {/* Header info */}
            <div className="flex justify-between items-start border-b border-slate-900 pb-4 mb-6">
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-rose-400">Attack Type: {result.attack}</span>
                <h3 className="text-2xl font-black text-white mt-1">Simulation Results</h3>
                <p className="text-xs text-slate-400 mt-1">{result.attack_description || "Analyzing multi-channel threat indicators..."}</p>
              </div>
              
              {result.resilience_verdict && (
                <div className={`px-4 py-2 rounded-xl border text-sm font-extrabold tracking-wider uppercase ${
                  result.resilience_verdict.includes("Detected") 
                    ? "bg-emerald-950/30 border-emerald-500/50 text-emerald-400 animate-pulse" 
                    : "bg-rose-950/30 border-rose-500/50 text-rose-400"
                }`}>
                  {result.resilience_verdict}
                </div>
              )}
            </div>

            {/* If Spoofed Biometrics or Graph Evasion */}
            {selectedAttack !== "BOILING_FROG" ? (
              <div className="grid gap-6 md:grid-cols-2">
                <div className="space-y-4">
                  <div className="bg-slate-900/50 border border-slate-900 p-4 rounded-2xl">
                    <span className="text-slate-400 text-xs uppercase tracking-wider">Simulated Trust Score</span>
                    <p className="text-4xl font-black text-white mt-1">{result.trust_score}</p>
                  </div>
                  <div className="bg-slate-900/50 border border-slate-900 p-4 rounded-2xl">
                    <span className="text-slate-400 text-xs uppercase tracking-wider">Dynamic Risk Level</span>
                    <p className="text-xl font-bold text-rose-400 mt-1">{result.trust_level}</p>
                  </div>
                </div>

                <div className="bg-slate-900/50 border border-slate-900 p-5 rounded-2xl">
                  <h4 className="text-slate-400 text-xs font-bold uppercase tracking-wider mb-3">Threat Engine Indicators</h4>
                  <ul className="space-y-2">
                    {result.explanation?.map((item: string, i: number) => (
                      <li key={i} className="text-sm text-slate-300 flex items-start gap-2">
                        <span className="text-rose-400 mt-0.5">⚠</span>
                        <span>{item}</span>
                      </li>
                    ))}
                    {!result.explanation && (
                      <li className="text-sm text-slate-500">Mule risk metrics propagated via shared graph community nodes.</li>
                    )}
                  </ul>
                </div>
              </div>
            ) : (
              /* Boiling Frog ATO Session Decay chart */
              <div className="space-y-6 animate-fadeIn">
                <div className="h-80 bg-slate-900/40 p-4 border border-slate-900 rounded-2xl">
                  <span className="text-slate-400 text-xs font-bold uppercase tracking-wider block mb-4">Trust Score Decay Over 15 Sessions</span>
                  <ResponsiveContainer width="100%" height="90%">
                    <LineChart data={result.sessions} margin={{ left: -10, right: 10 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                      <XAxis dataKey="session" stroke="#64748b" label={{ value: "Sessions", position: "insideBottomRight", offset: -5 }} />
                      <YAxis stroke="#64748b" domain={[0, 100]} />
                      <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155", borderRadius: "12px" }} />
                      <Line type="monotone" dataKey="trust_score" name="Session Trust Score" stroke="#ef4444" strokeWidth={3.5} dot={true} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>

                <div className="bg-slate-900/40 border border-slate-900 rounded-2xl p-4 overflow-x-auto">
                  <table className="w-full text-left border-collapse text-xs text-slate-300">
                    <thead>
                      <tr className="border-b border-slate-800 text-slate-500 font-bold uppercase">
                        <th className="py-2">Session</th>
                        <th>Biometric Match</th>
                        <th>Computed Trust</th>
                        <th>Level</th>
                        <th>Step-up Triggered</th>
                      </tr>
                    </thead>
                    <tbody>
                      {result.sessions.map((sess: any) => (
                        <tr key={sess.session} className="border-b border-slate-900/50 hover:bg-slate-900/30">
                          <td className="py-2.5 font-mono">{sess.session}</td>
                          <td>{Math.round(sess.biometric_score * 100)}%</td>
                          <td className="font-bold">{sess.trust_score}</td>
                          <td className={sess.trust_level === "BLOCKED" ? "text-red-400 font-bold" : "text-amber-400"}>{sess.trust_level}</td>
                          <td className={sess.step_up_triggered ? "text-amber-400 font-bold" : "text-slate-500"}>
                            {sess.step_up_triggered ? "Yes (OTP/Bio)" : "No"}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="h-full flex items-center justify-center border border-dashed border-slate-800 rounded-3xl p-8 text-center text-slate-500">
            <div>
              <svg className="mx-auto h-12 w-12 text-slate-600 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
              </svg>
              <p className="text-sm">Click Launch Simulation to execute adversarial red-team models.</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
