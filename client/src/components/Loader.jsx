import { useEffect, useState } from "react";

const steps = [
  "Analyzing ad creative…",
  "Extracting messaging & intent…",
  "Scraping landing page…",
  "Applying CRO principles…",
  "Personalizing content…",
  "Almost done…",
];

export default function Loader({ stage = 0 }) {
  const [tick, setTick] = useState(0);

  useEffect(() => {
    const id = setInterval(() => setTick((t) => t + 1), 80);
    return () => clearInterval(id);
  }, []);

  const dots = ".".repeat((tick % 3) + 1).padEnd(3, "\u00a0");
  const label = steps[Math.min(stage, steps.length - 1)];

  return (
    <div style={styles.wrap}>
      <div style={styles.ring}>
        <svg width="64" height="64" viewBox="0 0 64 64" style={{ animation: "spin 1s linear infinite" }}>
          <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
          <circle cx="32" cy="32" r="26" fill="none" stroke="rgba(200,240,74,0.15)" strokeWidth="3" />
          <circle cx="32" cy="32" r="26" fill="none" stroke="#c8f04a" strokeWidth="3"
            strokeDasharray="40 124" strokeLinecap="round" strokeDashoffset="0" />
        </svg>
      </div>
      <p style={styles.label}>{label}{dots}</p>
      <div style={styles.track}>
        <div style={{ ...styles.fill, width: `${((stage + 1) / steps.length) * 100}%` }} />
      </div>
    </div>
  );
}

const styles = {
  wrap: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: "20px",
    padding: "48px 0",
  },
  ring: { position: "relative" },
  label: {
    fontFamily: "var(--font-body)",
    fontSize: "14px",
    color: "var(--text-secondary)",
    letterSpacing: "0.02em",
    minWidth: "220px",
    textAlign: "center",
  },
  track: {
    width: "200px",
    height: "2px",
    background: "var(--border)",
    borderRadius: "2px",
    overflow: "hidden",
  },
  fill: {
    height: "100%",
    background: "var(--accent)",
    borderRadius: "2px",
    transition: "width 0.6s cubic-bezier(0.4,0,0.2,1)",
  },
};