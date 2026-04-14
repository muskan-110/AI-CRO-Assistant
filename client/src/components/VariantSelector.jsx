import { formatAdAnalysis } from "../utils/formatResponse";

export default function VariantSelector({ adAnalysis, onConfirm, onBack }) {
  const fields = formatAdAnalysis(adAnalysis);

  return (
    <div style={s.wrap}>
      <div style={s.header}>
        <span style={s.tag}>Ad Analysis</span>
        <h2 style={s.title}>We extracted this from your ad</h2>
        <p style={s.sub}>Review the detected intent before we personalize the landing page.</p>
      </div>

      <div style={s.card}>
        {fields.map(({ label, value }) => (
          <div key={label} style={s.row}>
            <span style={s.rowLabel}>{label}</span>
            <span style={s.rowValue}>{value}</span>
          </div>
        ))}
      </div>

      <div style={s.actions}>
        <button onClick={onBack} style={s.backBtn}>← Back</button>
        <button onClick={onConfirm} style={s.confirmBtn}>
          Looks good — personalize page →
        </button>
      </div>
    </div>
  );
}

const s = {
  wrap: { display: "flex", flexDirection: "column", gap: "28px" },
  header: { display: "flex", flexDirection: "column", gap: "8px" },
  tag: {
    display: "inline-block", fontSize: "11px", fontWeight: "600", letterSpacing: "0.08em",
    textTransform: "uppercase", color: "var(--accent)", background: "var(--accent-dim)",
    padding: "4px 10px", borderRadius: "99px", border: "1px solid rgba(200,240,74,0.25)",
    width: "fit-content",
  },
  title: { fontSize: "22px", fontWeight: "700", fontFamily: "var(--font-display)", color: "var(--text-primary)" },
  sub: { fontSize: "14px", color: "var(--text-secondary)" },
  card: {
    background: "var(--bg-surface)", borderRadius: "14px",
    border: "1px solid var(--border)", overflow: "hidden",
  },
  row: {
    display: "flex", justifyContent: "space-between", alignItems: "flex-start",
    padding: "14px 20px", borderBottom: "1px solid var(--border)", gap: "16px",
  },
  rowLabel: { fontSize: "13px", color: "var(--text-muted)", flexShrink: 0, paddingTop: "1px" },
  rowValue: { fontSize: "14px", color: "var(--text-primary)", textAlign: "right", lineHeight: "1.4" },
  actions: { display: "flex", gap: "12px" },
  backBtn: {
    padding: "12px 20px", fontSize: "14px", background: "none",
    border: "1px solid var(--border)", borderRadius: "10px",
    color: "var(--text-secondary)", cursor: "pointer", fontFamily: "var(--font-body)",
  },
  confirmBtn: {
    flex: 1, padding: "13px 24px", fontSize: "15px", fontWeight: "600",
    background: "var(--accent)", color: "#0a0a0f", border: "none",
    borderRadius: "10px", cursor: "pointer", fontFamily: "var(--font-display)",
    letterSpacing: "0.01em",
  },
};