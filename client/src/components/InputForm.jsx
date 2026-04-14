import { useState, useRef } from "react";

export default function InputForm({ onSubmit, loading }) {
  const [adMode, setAdMode] = useState("upload"); // "upload" | "url"
  const [adFile, setAdFile] = useState(null);
  const [adUrl, setAdUrl] = useState("");
  const [landingUrl, setLandingUrl] = useState("");
  const [dragOver, setDragOver] = useState(false);
  const fileRef = useRef(null);

  const handleFile = (file) => {
    if (!file) return;
    if (!file.type.startsWith("image/")) return;
    setAdFile(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    handleFile(e.dataTransfer.files[0]);
  };

  const canSubmit =
    landingUrl.trim() &&
    (adMode === "upload" ? adFile !== null : adUrl.trim() !== "");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!canSubmit || loading) return;
    onSubmit({
      adCreative: adMode === "upload" ? { file: adFile } : { url: adUrl.trim() },
      landingUrl: landingUrl.trim(),
    });
  };

  return (
    <form onSubmit={handleSubmit} style={s.form}>
      {/* Ad Creative */}
      <div style={s.field}>
        <div style={s.labelRow}>
          <span style={s.label}>Ad Creative</span>
          <div style={s.toggle}>
            <button
              type="button"
              style={{ ...s.tab, ...(adMode === "upload" ? s.tabActive : {}) }}
              onClick={() => setAdMode("upload")}
            >
              Upload
            </button>
            <button
              type="button"
              style={{ ...s.tab, ...(adMode === "url" ? s.tabActive : {}) }}
              onClick={() => setAdMode("url")}
            >
              URL
            </button>
          </div>
        </div>

        {adMode === "upload" ? (
          <div
            style={{
              ...s.dropzone,
              ...(dragOver ? s.dropzoneActive : {}),
              ...(adFile ? s.dropzoneFilled : {}),
            }}
            onClick={() => fileRef.current?.click()}
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
          >
            <input
              ref={fileRef}
              type="file"
              accept="image/*"
              style={{ display: "none" }}
              onChange={(e) => handleFile(e.target.files[0])}
            />
            {adFile ? (
              <div style={s.filePreview}>
                <img
                  src={URL.createObjectURL(adFile)}
                  alt="Ad preview"
                  style={s.previewImg}
                />
                <div style={s.fileInfo}>
                  <span style={s.fileName}>{adFile.name}</span>
                  <button
                    type="button"
                    style={s.removeBtn}
                    onClick={(e) => { e.stopPropagation(); setAdFile(null); }}
                  >
                    Remove
                  </button>
                </div>
              </div>
            ) : (
              <div style={s.dropPlaceholder}>
                <UploadIcon />
                <span style={s.dropText}>Drop image or click to browse</span>
                <span style={s.dropHint}>PNG, JPG, GIF, WEBP</span>
              </div>
            )}
          </div>
        ) : (
          <input
            type="url"
            placeholder="https://cdn.example.com/ad-creative.png"
            value={adUrl}
            onChange={(e) => setAdUrl(e.target.value)}
            style={s.input}
          />
        )}
      </div>

      {/* Landing Page URL */}
      <div style={s.field}>
        <label style={s.label}>Landing Page URL</label>
        <input
          type="url"
          placeholder="https://yourproduct.com/landing"
          value={landingUrl}
          onChange={(e) => setLandingUrl(e.target.value)}
          style={s.input}
          required
        />
        <span style={s.hint}>
          We'll scrape this page and personalize it to match your ad.
        </span>
      </div>

      <button type="submit" disabled={!canSubmit || loading} style={{
        ...s.submitBtn,
        ...(!canSubmit || loading ? s.submitDisabled : {}),
      }}>
        {loading ? "Generating…" : "Generate Personalized Page →"}
      </button>
    </form>
  );
}

function UploadIcon() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ color: "var(--text-muted)", marginBottom: "8px" }}>
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
      <polyline points="17 8 12 3 7 8" />
      <line x1="12" y1="3" x2="12" y2="15" />
    </svg>
  );
}

const s = {
  form: { display: "flex", flexDirection: "column", gap: "28px" },
  field: { display: "flex", flexDirection: "column", gap: "8px" },
  labelRow: { display: "flex", alignItems: "center", justifyContent: "space-between" },
  label: { fontSize: "13px", fontWeight: "500", color: "var(--text-secondary)", letterSpacing: "0.04em", textTransform: "uppercase" },
  hint: { fontSize: "12px", color: "var(--text-muted)" },
  toggle: { display: "flex", background: "var(--bg)", borderRadius: "8px", padding: "2px", border: "1px solid var(--border)" },
  tab: { padding: "4px 14px", fontSize: "12px", fontWeight: "500", border: "none", borderRadius: "6px", cursor: "pointer", background: "transparent", color: "var(--text-muted)", fontFamily: "var(--font-body)", transition: "all 0.15s" },
  tabActive: { background: "var(--bg-surface)", color: "var(--text-primary)", border: "1px solid var(--border-mid)" },
  input: {
    padding: "12px 16px", fontSize: "14px", background: "var(--bg-surface)",
    border: "1px solid var(--border)", borderRadius: "10px", color: "var(--text-primary)",
    fontFamily: "var(--font-body)", outline: "none", transition: "border 0.2s",
    width: "100%",
  },
  dropzone: {
    border: "1px dashed var(--border-mid)", borderRadius: "12px",
    padding: "28px", cursor: "pointer", transition: "all 0.2s",
    background: "var(--bg-surface)", minHeight: "100px",
    display: "flex", alignItems: "center", justifyContent: "center",
  },
  dropzoneActive: { border: "1px dashed var(--accent)", background: "var(--accent-dim)" },
  dropzoneFilled: { border: "1px solid var(--border-mid)", padding: "16px" },
  dropPlaceholder: { display: "flex", flexDirection: "column", alignItems: "center", gap: "4px" },
  dropText: { fontSize: "14px", color: "var(--text-secondary)" },
  dropHint: { fontSize: "12px", color: "var(--text-muted)" },
  filePreview: { display: "flex", alignItems: "center", gap: "16px", width: "100%" },
  previewImg: { width: "64px", height: "64px", objectFit: "cover", borderRadius: "8px", border: "1px solid var(--border)" },
  fileInfo: { display: "flex", flexDirection: "column", gap: "6px" },
  fileName: { fontSize: "13px", color: "var(--text-primary)", maxWidth: "240px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" },
  removeBtn: { fontSize: "12px", color: "var(--text-muted)", background: "none", border: "none", cursor: "pointer", padding: 0, fontFamily: "var(--font-body)", textDecoration: "underline" },
  submitBtn: {
    marginTop: "4px", padding: "14px 28px", fontSize: "15px", fontWeight: "600",
    background: "var(--accent)", color: "#0a0a0f", border: "none",
    borderRadius: "10px", cursor: "pointer", fontFamily: "var(--font-display)",
    letterSpacing: "0.01em", transition: "opacity 0.2s, transform 0.15s",
  },
  submitDisabled: { opacity: 0.35, cursor: "not-allowed" },
};