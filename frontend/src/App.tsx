import React from "react";
import { NavLink, Navigate, Route, Routes } from "react-router-dom";
import { DashboardPage } from "./pages/DashboardPage";
import { LoginPage } from "./pages/LoginPage";
import { TransferPage } from "./pages/TransferPage";
import { TrustPassportPage } from "./pages/TrustPassportPage";
import { AdminDashboard } from "./pages/AdminDashboard";
import { GraphPage } from "./pages/GraphPage";
import { AdversarialDemo } from "./pages/AdversarialDemo";

const navLinkClass = ({ isActive }: { isActive: boolean }) =>
  `rounded-full px-4 py-2 text-sm transition ${isActive ? "bg-sky-500 text-white" : "text-slate-300 hover:bg-slate-800"}`;

export default function App() {
  return (
    <div className="min-h-screen px-4 py-6 text-slate-100 md:px-8">
      <header className="mx-auto mb-8 flex max-w-7xl items-center justify-between gap-4 rounded-3xl border border-slate-800 bg-slate-950/60 px-5 py-4 backdrop-blur">
        <div>
          <p className="text-xs uppercase tracking-[0.35em] text-sky-300">TrustFabric</p>
          <h1 className="text-xl font-semibold text-white">Adaptive Multi-Channel Banking Trust Layer</h1>
        </div>
        <nav className="flex flex-wrap gap-2">
          <NavLink to="/" className={navLinkClass} end>Login</NavLink>
          <NavLink to="/dashboard" className={navLinkClass}>Dashboard</NavLink>
          <NavLink to="/transfer" className={navLinkClass}>Transfer</NavLink>
          <NavLink to="/passport" className={navLinkClass}>Passport</NavLink>
          <NavLink to="/graph" className={navLinkClass}>Graph</NavLink>
          <NavLink to="/admin" className={navLinkClass}>Admin</NavLink>
          <NavLink to="/adversarial" className={navLinkClass}>Adversarial</NavLink>
        </nav>
      </header>

      <main className="mx-auto max-w-7xl pb-12">
        <Routes>
          <Route path="/" element={<LoginPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/transfer" element={<TransferPage />} />
          <Route path="/passport" element={<TrustPassportPage />} />
          <Route path="/admin" element={<AdminDashboard />} />
          <Route path="/graph" element={<GraphPage />} />
          <Route path="/adversarial" element={<AdversarialDemo />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  );
}
