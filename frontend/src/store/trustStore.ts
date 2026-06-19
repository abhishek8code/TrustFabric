import { create } from "zustand";

type TrustState = {
  token: string | null;
  score: number;
  level: string;
  setTrust: (next: { token?: string | null; score?: number; level?: string }) => void;
};

export const useTrustStore = create<TrustState>((set) => ({
  token: localStorage.getItem("trust_token"),
  score: 72,
  level: "MEDIUM",
  setTrust: (next) =>
    set((state) => {
      const token = next.token ?? state.token;
      if (typeof next.token !== "undefined") {
        if (token) localStorage.setItem("trust_token", token);
        else localStorage.removeItem("trust_token");
      }
      return {
        token,
        score: next.score ?? state.score,
        level: next.level ?? state.level,
      };
    }),
}));
