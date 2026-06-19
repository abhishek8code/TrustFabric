import React, { useState, useRef } from "react";
import { api } from "../api/client";
import { useTrustStore } from "../store/trustStore";
import { StepUpModal } from "../components/StepUpModal";

interface KeyEventRecord {
  type: "down" | "up";
  key: string;
  time: number;
}

export const LoginPage: React.FC = () => {
  const setTrust = useTrustStore((state) => state.setTrust);
  const [customerId, setCustomerId] = useState("cust_001");
  const [password, setPassword] = useState("");
  const [status, setStatus] = useState<string>("");
  const [errorMsg, setErrorMsg] = useState<string>("");
  
  // Step-up verification state
  const [showStepUp, setShowStepUp] = useState(false);
  const [stepUpType, setStepUpType] = useState<"OTP" | "BIOMETRIC">("OTP");
  const [stepUpSessionId, setStepUpSessionId] = useState("");
  
  // Track key press events for keystroke dynamics
  const keyEvents = useRef<KeyEventRecord[]>([]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    keyEvents.current.push({
      type: "down",
      key: e.key,
      time: performance.now(),
    });
  };

  const handleKeyUp = (e: React.KeyboardEvent<HTMLInputElement>) => {
    keyEvents.current.push({
      type: "up",
      key: e.key,
      time: performance.now(),
    });
  };

  const login = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus("Verifying credentials and biometrics...");
    setErrorMsg("");

    let keystrokeTimings: number[] | null = null;
    let keystrokeHoldTimes: number[] | null = null;

    // We expect exactly 11 keys in sequence: ['.', 't', 'i', 'e', '5', 'R', 'o', 'a', 'n', 'l', 'Enter']
    // Let's attempt to extract CMU timing features if password is typed
    try {
      const events = keyEvents.current;
      const expectedKeys = [".", "t", "i", "e", "5", "R", "o", "a", "n", "l", "Enter"];
      
      const downs: { [key: string]: number } = {};
      const ups: { [key: string]: number } = {};
      
      // Extract first occurrence of key down/up for simplicity
      events.forEach((evt) => {
        if (evt.type === "down" && downs[evt.key] === undefined) {
          downs[evt.key] = evt.time;
        } else if (evt.type === "up" && ups[evt.key] === undefined) {
          ups[evt.key] = evt.time;
        }
      });

      // Check if we captured all keys
      const hasAllKeys = expectedKeys.every(k => downs[k] !== undefined && ups[k] !== undefined);

      if (hasAllKeys) {
        // Build 11 Holds (H)
        const holds = expectedKeys.map(k => ups[k] - downs[k]);
        
        // Build 10 Down-Downs (DD)
        const dds: number[] = [];
        // Build 10 Up-Downs (UD)
        const uds: number[] = [];

        for (let i = 0; i < expectedKeys.length - 1; i++) {
          const k1 = expectedKeys[i];
          const k2 = expectedKeys[i + 1];
          dds.push(downs[k2] - downs[k1]);
          uds.push(downs[k2] - ups[k1]);
        }

        keystrokeHoldTimes = holds; // H.key holds
        keystrokeTimings = [...dds, ...uds]; // Latencies
        console.log("✓ Biometrics captured successfully:", holds.length + dds.length + uds.length, "features");
      }
    } catch (err) {
      console.warn("Failed to parse keystroke dynamics: ", err);
    }

    try {
      const response = await api.post("/auth/login", {
        customer_id: customerId,
        password_hash: "demo",
        channel: "web",
        device_fingerprint: "dev_web_bob_demo",
        ip_address: "192.168.1.15",
        keystroke_timings: keystrokeTimings,
        keystroke_hold_times: keystrokeHoldTimes,
      });

      if (response.data.step_up_required === "OTP" || response.data.step_up_required === "BIOMETRIC") {
        setStepUpType(response.data.step_up_required);
        setStepUpSessionId(response.data.session_id || response.data.token);
        setShowStepUp(true);
        setStatus(`⚠ Additional verification required: ${response.data.step_up_required}`);
      } else {
        setTrust({
          token: response.data.token,
          score: response.data.trust_score,
          level: response.data.trust_level,
        });
        setStatus(`✓ Logged in. Trust Score: ${response.data.trust_score} (${response.data.trust_level})`);
      }
      keyEvents.current = []; // Reset events
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || "Authentication failed.");
      setStatus("");
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-[70vh]">
      <div className="w-full max-w-lg p-8 rounded-3xl border border-slate-800 bg-slate-950/70 backdrop-blur-md shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 left-0 w-full h-1.5 bg-gradient-to-r from-sky-500 via-indigo-500 to-purple-500" />
        
        <div className="text-center mb-6">
          <span className="text-xs font-bold uppercase tracking-[0.4em] text-sky-400">TrustFabric Layer</span>
          <h2 className="mt-2 text-3xl font-extrabold text-white tracking-tight">Adaptive Trust Gate</h2>
          <p className="mt-2 text-sm text-slate-400">
            Sign in below. The security engine calculates typing rhythms and device signals in real-time.
          </p>
        </div>

        <form onSubmit={login} className="space-y-5">
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Customer ID</label>
            <input
              type="text"
              value={customerId}
              onChange={(e) => setCustomerId(e.target.value)}
              className="w-full rounded-2xl border border-slate-800 bg-slate-900/60 px-4 py-3.5 text-white placeholder-slate-500 outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500 transition"
              required
            />
          </div>

          <div>
            <div className="flex justify-between items-center mb-2">
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-400">Password</label>
              <span className="text-[10px] text-slate-500 bg-slate-900 px-2 py-0.5 rounded">
                Try: <code className="text-sky-300 font-mono">.tie5Roanl</code> for genuine biometrics
              </span>
            </div>
            <input
              type="password"
              placeholder="••••••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onKeyDown={handleKeyDown}
              onKeyUp={handleKeyUp}
              className="w-full rounded-2xl border border-slate-800 bg-slate-900/60 px-4 py-3.5 text-white placeholder-slate-500 outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500 transition font-mono"
              required
            />
          </div>

          <button
            type="submit"
            className="w-full rounded-2xl bg-gradient-to-r from-sky-500 to-indigo-500 hover:from-sky-400 hover:to-indigo-400 py-3.5 font-bold text-white shadow-lg transition active:scale-[0.98]"
          >
            Authenticate & Issue Trust Token
          </button>
        </form>

        {status && (
          <div className="mt-4 p-3 rounded-2xl bg-emerald-950/50 border border-emerald-900/50 text-sm text-emerald-400 text-center animate-pulse">
            {status}
          </div>
        )}

        {errorMsg && (
          <div className="mt-4 p-3 rounded-2xl bg-rose-950/50 border border-rose-900/50 text-sm text-rose-400 text-center">
            {errorMsg}
          </div>
        )}
      </div>

      <StepUpModal
        open={showStepUp}
        type={stepUpType}
        sessionId={stepUpSessionId}
        onSuccess={(newToken, score, level) => {
          setTrust({ token: newToken, score, level });
          setShowStepUp(false);
          setStatus(`✓ Authenticated. Dynamic Trust Level: ${level} (${score})`);
        }}
        onClose={() => {
          setShowStepUp(false);
          setStatus("Authentication aborted.");
        }}
      />
    </div>
  );
};
