export default function ComparisonView({ originalUrl, score, changes }) {
  return (
    <div style={s.wrap}>
      <div style={s.statsRow}>
        <Stat label="CRO Score" value={`${score}/100`} accent />
        <Stat label="Changes applied" value={changes.length} />
        <Stat label="Source page" value={new URL(originalUrl).hostname} small />
      </div>
    </div>
  );
}

function Stat({ label, value, accent, small }) {
  return (
    <div style={s.stat}>
      <div style={{ ...s.statValue, ...(accent ? s.statAccent : {}), ...(small ? s.statSmall : {}) }}>
        {value}
      </div>
      <div style={s.statLabel}>{label}</div>
    </div>
  );
}

const s = {
  wrap: { padding: "0" },
  statsRow: {
    display: "grid", gridTemplateColumns: "repeat(3, 1fr)",
    gap: "12px",
  },
  stat: {
    background: "var(--bg-surface)", borderRadius: "12px",
    border: "1px solid var(--border)", padding: "16px",
    display: "flex", flexDirection: "column", gap: "4px",
  },
  statValue: {
    fontSize: "22px", fontWeight: "700", fontFamily: "var(--font-display)",
    color: "var(--text-primary)", lineHeight: 1.2,
  },
  statAccent: { color: "var(--accent)" },
  statSmall: { fontSize: "14px", fontWeight: "500" },
  statLabel: { fontSize: "12px", color: "var(--text-muted)" },
};