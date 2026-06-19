import React, { useEffect, useState } from "react";

interface TrustMeterProps {
  score: number;
  level: string;
  size?: number;
}

const LEVEL_COLORS: Record<string, string> = {
  HIGH: "#22c55e",
  MEDIUM: "#eab308",
  LOW: "#f97316",
  BLOCKED: "#ef4444",
};

export const TrustMeter: React.FC<TrustMeterProps> = ({ score, level, size = 180 }) => {
  const [displayScore, setDisplayScore] = useState(0);

  useEffect(() => {
    let current = 0;
    const interval = window.setInterval(() => {
      current += 2;
      if (current >= score) {
        setDisplayScore(score);
        window.clearInterval(interval);
      } else {
        setDisplayScore(current);
      }
    }, 16);
    return () => window.clearInterval(interval);
  }, [score]);

  const color = LEVEL_COLORS[level] ?? "#6b7280";
  const radius = 70;
  const cx = size / 2;
  const cy = size / 2;
  const circumference = 2 * Math.PI * radius;
  const dash = (displayScore / 100) * circumference;

  return (
    <div className="flex flex-col items-center gap-2">
      <svg width={size} height={size}>
        <circle cx={cx} cy={cy} r={radius} fill="none" stroke="#1e293b" strokeWidth={14} />
        <circle
          cx={cx}
          cy={cy}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={14}
          strokeDasharray={`${dash} ${circumference - dash}`}
          strokeLinecap="round"
          transform={`rotate(-90 ${cx} ${cy})`}
        />
        <text x={cx} y={cy - 8} textAnchor="middle" fill={color} fontSize={32} fontWeight={700} fontFamily="monospace">
          {Math.round(displayScore)}
        </text>
        <text x={cx} y={cy + 18} textAnchor="middle" fill="#94a3b8" fontSize={13} fontWeight={500}>
          {level}
        </text>
      </svg>
      <span className="text-sm text-slate-400 font-medium tracking-wider uppercase">Trust Score</span>
    </div>
  );
};
