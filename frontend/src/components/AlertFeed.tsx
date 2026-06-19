import React from "react";

export const AlertFeed: React.FC<{ alerts: Array<{ id: string; severity: string; message: string }> }> = ({ alerts }) => (
  <div className="glass rounded-2xl p-4">
    <h3 className="text-slate-200 font-semibold mb-4">SOC Alerts</h3>
    <div className="space-y-3">
      {alerts.map((alert) => (
        <div key={alert.id} className="rounded-xl border border-slate-700/70 bg-slate-950/40 p-3">
          <div className="flex items-center justify-between text-xs uppercase tracking-wider text-slate-400">
            <span>{alert.id}</span>
            <span>{alert.severity}</span>
          </div>
          <p className="mt-2 text-sm text-slate-200">{alert.message}</p>
        </div>
      ))}
    </div>
  </div>
);
