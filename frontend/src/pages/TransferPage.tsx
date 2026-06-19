import React, { useState } from "react";
import { api } from "../api/client";
import { ShapWaterfall, ShapFeature } from "../components/ShapWaterfall";

export const TransferPage: React.FC = () => {
  const [amount, setAmount] = useState<number>(15000);
  const [card1, setCard1] = useState<number>(10001);
  const [card2, setCard2] = useState<number>(555);
  const [pEmail, setPEmail] = useState<string>("gmail.com");
  const [rEmail, setREmail] = useState<string>("gmail.com");
  
  const [result, setResult] = useState<any>(null);
  const [errorMsg, setErrorMsg] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);

  const triggerTransfer = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg("");
    setResult(null);

    const token = localStorage.getItem("trust_token") ?? "";
    if (!token) {
      setErrorMsg("No active Trust Token found. Please login first to generate a token.");
      setLoading(false);
      return;
    }

    try {
      const response = await api.post("/transactions/score", {
        transaction_id: `TX-${Math.floor(1000 + Math.random() * 9000)}`,
        customer_id: "cust_001",
        trust_token: token,
        amount: Number(amount),
        product_cd: "W",
        card1: Number(card1),
        card2: Number(card2),
        card4: "visa",
        card6: "debit",
        p_emaildomain: pEmail,
        r_emaildomain: rEmail,
        d1: 12.0,
        d2: 12.0,
      });

      setResult(response.data);
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || "Transaction evaluation failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid gap-6 md:grid-cols-[1fr,1.2fr]">
      <div className="rounded-3xl border border-slate-800 bg-slate-950/70 p-6 backdrop-blur-md relative overflow-hidden">
        <div className="absolute top-0 left-0 w-full h-1.5 bg-gradient-to-r from-amber-500 to-orange-500" />
        
        <h2 className="text-2xl font-extrabold text-white tracking-tight mb-2">Simulate Bank Transfer</h2>
        <p className="text-xs text-slate-400 mb-6">Evaluate transaction risks dynamically through LightGBM scoring.</p>

        <form onSubmit={triggerTransfer} className="space-y-4 text-sm">
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5">
              Transfer Amount: INR {amount.toLocaleString()}
            </label>
            <input
              type="range"
              min="500"
              max="250000"
              step="500"
              value={amount}
              onChange={(e) => setAmount(Number(e.target.value))}
              className="w-full accent-amber-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1">Card Series (1)</label>
              <input
                type="number"
                value={card1}
                onChange={(e) => setCard1(Number(e.target.value))}
                className="w-full rounded-xl border border-slate-800 bg-slate-900 px-3 py-2 text-white outline-none focus:border-amber-500"
              />
            </div>
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1">Card Bank Code (2)</label>
              <input
                type="number"
                value={card2}
                onChange={(e) => setCard2(Number(e.target.value))}
                className="w-full rounded-xl border border-slate-800 bg-slate-900 px-3 py-2 text-white outline-none focus:border-amber-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1">Payer Email Domain</label>
              <select
                value={pEmail}
                onChange={(e) => setPEmail(e.target.value)}
                className="w-full rounded-xl border border-slate-800 bg-slate-900 px-3 py-2 text-white outline-none focus:border-amber-500"
              >
                <option value="gmail.com">gmail.com</option>
                <option value="yahoo.com">yahoo.com</option>
                <option value="bob.co.in">bob.co.in</option>
                <option value="temp-mail.org">temp-mail.org</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1">Recip. Email Domain</label>
              <select
                value={rEmail}
                onChange={(e) => setREmail(e.target.value)}
                className="w-full rounded-xl border border-slate-800 bg-slate-900 px-3 py-2 text-white outline-none focus:border-amber-500"
              >
                <option value="gmail.com">gmail.com</option>
                <option value="yahoo.com">yahoo.com</option>
                <option value="bob.co.in">bob.co.in</option>
                <option value="temp-mail.org">temp-mail.org</option>
              </select>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-xl bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-400 hover:to-orange-400 py-3 font-bold text-slate-950 shadow-md transition active:scale-[0.98]"
          >
            {loading ? "Evaluating Risk..." : "Evaluate Transaction"}
          </button>
        </form>

        {errorMsg && (
          <div className="mt-4 p-3 rounded-xl bg-rose-950/50 border border-rose-900/50 text-xs text-rose-400 text-center">
            {errorMsg}
          </div>
        )}
      </div>

      <div className="space-y-6">
        {result ? (
          <>
            <div className={`rounded-3xl border p-6 relative overflow-hidden backdrop-blur-md ${
              result.action === "ALLOW"
                ? "bg-emerald-950/20 border-emerald-800/50"
                : result.action === "STEP_UP"
                ? "bg-amber-950/20 border-amber-800/50"
                : "bg-rose-950/20 border-rose-800/50"
            }`}>
              <h3 className="text-xl font-bold text-white mb-4">Risk Evaluation Result</h3>
              
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-slate-400 text-xs">DECISION</span>
                  <p className={`text-2xl font-black mt-1 ${
                    result.action === "ALLOW" ? "text-emerald-400" : result.action === "STEP_UP" ? "text-amber-400" : "text-rose-400"
                  }`}>{result.action}</p>
                </div>
                <div>
                  <span className="text-slate-400 text-xs">FRAUD PROBABILITY</span>
                  <p className="text-2xl font-black mt-1 text-slate-200">{Math.round(result.fraud_probability * 100)}%</p>
                </div>
                <div>
                  <span className="text-slate-400 text-xs">TRUST DEGRADATION</span>
                  <p className="text-lg font-bold mt-1 text-rose-400">-{result.trust_degradation} points</p>
                </div>
                <div>
                  <span className="text-slate-400 text-xs">FLAGGED</span>
                  <p className="text-lg font-bold mt-1 text-slate-200">{result.is_flagged ? "Yes" : "No"}</p>
                </div>
              </div>
            </div>

            <ShapWaterfall features={result.shap_explanation as ShapFeature[]} />
          </>
        ) : (
          <div className="h-full flex items-center justify-center border border-dashed border-slate-800 rounded-3xl p-8 text-center text-slate-500">
            <div>
              <svg className="mx-auto h-12 w-12 text-slate-600 mb-2 animate-pulse" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
              <p className="text-sm">Submit evaluation to see model explainability results.</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
