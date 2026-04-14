import { useState } from "react";
import { truncateUrl } from "../utils/formatResponse";

export default function PreviewPanel({ personalizedHtml, originalUrl, changes, score, onReset }) {
  const [mode, setMode] = useState("personalized");
  const [originalFailed, setOriginalFailed] = useState(false);

  // Use srcdoc instead of blob URL — prevents iframe navigation issues
  // clicking links inside won't navigate the iframe away
  // const handleIframeClick = (e) => e.preventDefault();

  return (
    <div style={s.root}>
      {/* Top bar */}
      <div style={s.topbar}>
        <div style={s.topLeft}>
          <button onClick={onReset} style={s.backBtn}>
            <ChevronLeft /> Back
          </button>
          <span style={s.urlBadge}>{truncateUrl(originalUrl)}</span>
        </div>
        <div style={s.modeToggle}>
          {[
            { id: "personalized", label: "Personalized" },
            { id: "split", label: "Compare" },
            { id: "original", label: "Original" },
          ].map(({ id, label }) => (
            <button
              key={id}
              style={{ ...s.modeBtn, ...(mode === id ? s.modeBtnActive : {}) }}
              onClick={() => setMode(id)}
            >
              {label}
            </button>
          ))}
        </div>
        <div style={s.scoreChip}>
          <span style={s.scoreNum}>{score}</span>
          <span style={s.scoreLabel}>CRO score</span>
        </div>
      </div>

      {/* Preview area */}
      <div style={s.previewArea}>
        {mode === "split" ? (
          <div style={s.splitWrap}>
            <div style={s.splitPane}>
              <div style={s.paneLabel}>Original</div>
              {originalFailed ? (
                <IframeBlockedFallback url={originalUrl} />
              ) : (
                <iframe
                  src={originalUrl}
                  title="Original"
                  style={s.iframe}
                  sandbox="allow-scripts allow-same-origin"
                  onError={() => setOriginalFailed(true)}
                  onLoad={(e) => {
                    try {
                      const doc = e.target.contentDocument;
                      if (!doc || doc.body?.innerHTML === "") setOriginalFailed(true);
                    } catch { setOriginalFailed(true); }
                  }}
                />
              )}
            </div>
            <div style={s.divider} />
            <div style={s.splitPane}>
              <div style={{ ...s.paneLabel, color: "var(--accent)" }}>Personalized</div>
              {/* srcdoc prevents navigation when links are clicked */}
              <iframe
                srcDoc={personalizedHtml}
                title="Personalized"
                style={s.iframe}
                sandbox="allow-scripts allow-popups"
              />
            </div>
          </div>
        ) : mode === "personalized" ? (
          <iframe
            srcDoc={personalizedHtml}
            title="Personalized"
            style={s.iframeFull}
            sandbox="allow-scripts allow-popups"
          />
        ) : originalFailed ? (
          <IframeBlockedFallback url={originalUrl} fullScreen />
        ) : (
          <iframe
            src={originalUrl}
            title="Original"
            style={s.iframeFull}
            sandbox="allow-scripts allow-same-origin"
            onError={() => setOriginalFailed(true)}
            onLoad={(e) => {
              try {
                const doc = e.target.contentDocument;
                if (!doc || doc.body?.innerHTML === "") setOriginalFailed(true);
              } catch { setOriginalFailed(true); }
            }}
          />
        )}
      </div>

      {/* Sidebar */}
      <div style={s.sidebar}>
        <h3 style={s.sidebarTitle}>What changed</h3>
        {originalFailed && (
          <div style={s.iframeWarning}>
            <span style={s.warningIcon}>⚠</span>
            <span>
              Original page blocks iframe embedding (X-Frame-Options).
              This is a browser security restriction — the personalized version is unaffected.
            </span>
          </div>
        )}
        <ul style={s.changesList}>
          {changes.map((c, i) => (
            <li key={i} style={s.changeItem}>
              <span style={s.changeDot} />
              <span>{c}</span>
            </li>
          ))}
        </ul>
        <button
          style={s.downloadBtn}
          onClick={() => {
            const blob = new Blob([personalizedHtml], { type: "text/html" });
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = "personalized-landing.html";
            a.click();
            URL.revokeObjectURL(url);
          }}
        >
          Download HTML
        </button>
      </div>
    </div>
  );
}

function IframeBlockedFallback({ url, fullScreen }) {
  return (
    <div style={{ ...s.fallbackWrap, ...(fullScreen ? { height: "100%" } : {}) }}>
      <div style={s.fallbackIcon}>🔒</div>
      <p style={s.fallbackTitle}>Original page blocked</p>
      <p style={s.fallbackSub}>
        <strong>{new URL(url).hostname}</strong> uses X-Frame-Options / CSP headers
        that prevent embedding in iframes. This is a browser security policy set by
        the website — it does not affect the personalized version.
      </p>
      <a href={url} target="_blank" rel="noopener noreferrer" style={s.fallbackLink}>
        Open original in new tab →
      </a>
    </div>
  );
}

function ChevronLeft() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
      strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="15 18 9 12 15 6" />
    </svg>
  );
}

const s = {
  root: {
    position: "fixed", inset: 0, background: "var(--bg)",
    display: "grid", gridTemplateRows: "56px 1fr", gridTemplateColumns: "1fr 280px",
    gridTemplateAreas: `"topbar topbar" "preview sidebar"`,
    fontFamily: "var(--font-body)",
  },
  topbar: {
    gridArea: "topbar", display: "flex", alignItems: "center",
    justifyContent: "space-between", padding: "0 20px",
    borderBottom: "1px solid var(--border)", background: "var(--bg-card)", gap: "16px",
  },
  topLeft: { display: "flex", alignItems: "center", gap: "12px", minWidth: 0 },
  backBtn: {
    display: "flex", alignItems: "center", gap: "4px", background: "none",
    border: "1px solid var(--border)", borderRadius: "8px", color: "var(--text-secondary)",
    fontSize: "13px", padding: "6px 12px", cursor: "pointer", fontFamily: "var(--font-body)",
    whiteSpace: "nowrap",
  },
  urlBadge: {
    fontSize: "12px", color: "var(--text-muted)", background: "var(--bg-surface)",
    padding: "4px 10px", borderRadius: "6px", border: "1px solid var(--border)",
    overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", maxWidth: "280px",
  },
  modeToggle: {
    display: "flex", background: "var(--bg-surface)", borderRadius: "10px",
    padding: "3px", border: "1px solid var(--border)", gap: "2px",
  },
  modeBtn: {
    padding: "6px 16px", fontSize: "13px", fontWeight: "500", border: "none",
    borderRadius: "8px", cursor: "pointer", background: "transparent",
    color: "var(--text-muted)", fontFamily: "var(--font-body)", transition: "all 0.15s",
  },
  modeBtnActive: {
    background: "var(--bg-card)", color: "var(--text-primary)",
    border: "1px solid var(--border-mid)",
  },
  scoreChip: { display: "flex", flexDirection: "column", alignItems: "flex-end", minWidth: "60px" },
  scoreNum: { fontSize: "20px", fontWeight: "700", color: "var(--accent)", fontFamily: "var(--font-display)", lineHeight: 1 },
  scoreLabel: { fontSize: "10px", color: "var(--text-muted)", letterSpacing: "0.05em", textTransform: "uppercase" },
  previewArea: { gridArea: "preview", overflow: "hidden", background: "#fff" },
  iframeFull: { width: "100%", height: "100%", border: "none", display: "block" },
  splitWrap: { display: "flex", height: "100%" },
  splitPane: { flex: 1, position: "relative", overflow: "hidden" },
  paneLabel: {
    position: "relative", top: "12px", left: "50%", transform: "translateX(-50%)",
    fontSize: "11px", fontWeight: "600", letterSpacing: "0.06em", textTransform: "uppercase",
    background: "rgba(10,10,15,0.8)", color: "var(--text-secondary)",
    padding: "4px 12px", borderRadius: "99px", zIndex: 2, border: "1px solid var(--border)",
  },
  iframe: { width: "100%", height: "100%", border: "none", display: "block" },
  divider: { width: "1px", background: "var(--border-mid)", flexShrink: 0 },
  sidebar: {
    gridArea: "sidebar", padding: "24px 20px", borderLeft: "1px solid var(--border)",
    overflowY: "auto", display: "flex", flexDirection: "column", gap: "16px",
    background: "var(--bg-card)",
  },
  sidebarTitle: {
    fontSize: "13px", fontWeight: "600", color: "var(--text-secondary)",
    letterSpacing: "0.04em", textTransform: "uppercase",
  },
  iframeWarning: {
    display: "flex", gap: "8px", alignItems: "flex-start",
    background: "rgba(239,153,39,0.1)", border: "1px solid rgba(239,153,39,0.3)",
    borderRadius: "8px", padding: "10px 12px", fontSize: "11px",
    color: "var(--text-secondary)", lineHeight: 1.5,
  },
  warningIcon: { fontSize: "14px", flexShrink: 0 },
  changesList: { listStyle: "none", display: "flex", flexDirection: "column", gap: "12px", flex: 1 },
  changeItem: {
    display: "flex", alignItems: "flex-start", gap: "10px",
    fontSize: "13px", color: "var(--text-primary)", lineHeight: "1.5",
  },
  changeDot: {
    width: "6px", height: "6px", borderRadius: "50%",
    background: "var(--accent)", flexShrink: 0, marginTop: "6px",
  },
  downloadBtn: {
    display: "block", textAlign: "center", padding: "11px 16px",
    background: "var(--accent-dim)", color: "var(--accent)",
    border: "1px solid rgba(200,240,74,0.3)", borderRadius: "10px",
    fontSize: "13px", fontWeight: "600", cursor: "pointer",
    fontFamily: "var(--font-body)", letterSpacing: "0.02em",
  },
  fallbackWrap: {
    display: "flex", flexDirection: "column", alignItems: "center",
    justifyContent: "center", padding: "48px 32px", textAlign: "center",
    background: "#f8f8f8", height: "100%", gap: "12px",
  },
  fallbackIcon: { fontSize: "40px", marginBottom: "8px" },
  fallbackTitle: { fontSize: "16px", fontWeight: "700", color: "#111" },
  fallbackSub: { fontSize: "13px", color: "#666", maxWidth: "320px", lineHeight: 1.6 },
  fallbackLink: {
    marginTop: "8px", fontSize: "13px", color: "#2563eb", fontWeight: "600",
    textDecoration: "none", padding: "8px 16px", border: "1px solid #2563eb", borderRadius: "8px",
  },
};