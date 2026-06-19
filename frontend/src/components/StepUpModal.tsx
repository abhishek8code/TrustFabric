import React, { useState } from "react";
import { api } from "../api/client";

interface StepUpModalProps {
  open: boolean;
  type: "OTP" | "BIOMETRIC";
  sessionId: string;
  onSuccess: (newToken: string, score: number, level: string) => void;
  onClose: () => void;
}

export const StepUpModal: React.FC<StepUpModalProps> = ({ open, type, sessionId, onSuccess, onClose }) => {
  const [loading, setLoading] = useState(false);
  const [otp, setOtp] = useState("");
  const [errorMsg, setErrorMsg] = useState("");

  if (!open) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg("");

    try {
      const response = await api.post("/auth/step-up", {
        session_id: sessionId,
        step_up_type: type,
        otp_value: type === "OTP" ? otp : undefined,
        biometric_payload: type === "BIOMETRIC" ? { verified: true } : undefined,
      });

      onSuccess(response.data.token, response.data.trust_score, response.data.trust_level);
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || "Step-up verification failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4">
      <div className="glass max-w-md w-full rounded-3xl p-6 border border-slate-800 shadow-glow relative overflow-hidden">
        <div className="absolute top-0 left-0 w-full h-1.5 bg-gradient-to-r from-sky-500 to-indigo-500" />
        
        <p className="text-xs uppercase tracking-[0.3em] text-sky-400 font-bold">Multi-Factor Verification</p>
        <h3 className="mt-2 text-2xl font-extrabold text-white">Verify Your Action</h3>
        <p className="mt-2 text-sm text-slate-400">
          {type === "OTP"
            ? "A verification code has been sent to your registered mobile number."
            : "Please complete your biometric fingerprint/touch check."}
        </p>

        <form onSubmit={handleSubmit} className="mt-5 space-y-4">
          {type === "OTP" && (
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5">Enter 6-Digit OTP</label>
              <input
                type="text"
                placeholder="123456"
                value={otp}
                onChange={(e) => setOtp(e.target.value)}
                maxLength={6}
                className="w-full text-center tracking-[0.5em] font-mono text-xl rounded-2xl border border-slate-800 bg-slate-900 px-4 py-3 text-white placeholder-slate-600 outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500"
                required
              />
            </div>
          )}

          <div className="flex gap-3">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 rounded-2xl bg-sky-500 hover:bg-sky-400 py-3 font-bold text-white transition active:scale-[0.98]"
            >
              {loading ? "Verifying..." : type === "OTP" ? "Submit OTP" : "Simulate Biometrics"}
            </button>
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-3 rounded-2xl border border-slate-800 text-sm font-semibold text-slate-300 hover:bg-slate-900"
            >
              Cancel
            </button>
          </div>
        </form>

        {errorMsg && (
          <div className="mt-4 p-3 rounded-xl bg-rose-950/50 border border-rose-900/50 text-xs text-rose-400 text-center">
            {errorMsg}
          </div>
        )}
      </div>
    </div>
  );
};
