import { useState } from "react";
import InputForm from "../components/InputForm";
import Loader from "../components/Loader";
import VariantSelector from "../components/VariantSelector";
import PreviewPanel from "../components/PreviewPanel";
import { analyzeAdCreative, scrapeLandingPage, generatePersonalizedPage } from "../services/api";
import { formatPersonalizationResult } from "../utils/formatResponse";

// Steps: "input" → "analyzing" → "review" → "generating" → "preview"

export default function Home() {
  const [step, setStep] = useState("input");
  const [loaderStage, setLoaderStage] = useState(0);
  const [error, setError] = useState(null);

  const [inputData, setInputData] = useState(null);
  const [adAnalysis, setAdAnalysis] = useState(null);
  const [pageData, setPageData] = useState(null);
  const [result, setResult] = useState(null);

  const handleFormSubmit = async ({ adCreative, landingUrl }) => {
    setError(null);
    setInputData({ adCreative, landingUrl });
    setStep("analyzing");
    setLoaderStage(0);

    try {
      const [analysis, page] = await Promise.all([
        analyzeAdCreative(adCreative),
        (async () => {
          setLoaderStage(1);
          return scrapeLandingPage(landingUrl);
        })(),
      ]);
      setLoaderStage(2);
      setAdAnalysis(analysis);
      setPageData(page);
      setStep("review");
    } catch (err) {
        console.log(err)
      setError("Failed to analyze ad or fetch the landing page. Please try again.");
      setStep("input");
    }
  };

  const handleConfirmGenerate = async () => {
    setError(null);
    setStep("generating");
    setLoaderStage(3);

    try {
      await new Promise((r) => setTimeout(r, 400));
      setLoaderStage(4);
      const raw = await generatePersonalizedPage({
        adAnalysis,
        pageData,
        landingUrl: inputData.landingUrl,
      });
      setLoaderStage(5);
      const formatted = formatPersonalizationResult(raw);
      setResult(formatted);
      setTimeout(() => setStep("preview"), 400);
    } catch (err) {
        console.error(err)
      setError("Page generation failed. Please try again.");
      setStep("review");
    }
  };

  const handleReset = () => {
    setStep("input");
    setAdAnalysis(null);
    setPageData(null);
    setResult(null);
    setInputData(null);
    setError(null);
    setLoaderStage(0);
  };

  if (step === "preview" && result) {
    return (
      <PreviewPanel
        personalizedHtml={result.html}
        originalUrl={inputData.landingUrl}
        changes={result.changes}
        score={result.score}
        onReset={handleReset}
      />
    );
  }

  return (
    <div style={layout.page}>
      <div style={layout.content}>
        {/* Header */}
        <header style={layout.header}>
          <div style={layout.logoRow}>
            <LogoMark />
            <span style={layout.logoText}>AdPersonalize</span>
            <span style={layout.betaBadge}>beta</span>
          </div>
          <h1 style={layout.headline}>
            Turn your ad creative into<br />
            <em style={layout.headlineAccent}>a personalized landing page</em>
          </h1>
          <p style={layout.tagline}>
            Drop in an ad + a landing page URL. We'll analyze the ad's intent and rewrite
            the page with CRO best practices — message-matched to your creative.
          </p>
        </header>

        {/* Main card */}
        <div style={layout.card}>
          {error && <div style={layout.error}>{error}</div>}

          {(step === "analyzing" || step === "generating") && (
            <Loader stage={loaderStage} />
          )}

          {step === "input" && (
            <InputForm onSubmit={handleFormSubmit} loading={false} />
          )}

          {step === "review" && adAnalysis && (
            <VariantSelector
              adAnalysis={adAnalysis}
              onConfirm={handleConfirmGenerate}
              onBack={handleReset}
            />
          )}
        </div>


        <footer style={layout.footer}>
          
        </footer>
      </div>
    </div>
  );
}

function LogoMark() {
  return (
    <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
      <rect width="28" height="28" rx="8" fill="#c8f04a" />
      <path d="M8 20 L14 8 L20 20 M10.5 15.5 H17.5" stroke="#0a0a0f" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}

const layout = {
  page: {
    minHeight: "100vh", display: "flex", alignItems: "flex-start",
    justifyContent: "center", padding: "60px 20px 80px",
    background: "var(--bg)",
  },
  content: { width: "100%", maxWidth: "520px", display: "flex", flexDirection: "column", gap: "36px" },
  header: { display: "flex", flexDirection: "column", gap: "16px" },
  logoRow: { display: "flex", alignItems: "center", gap: "10px" },
  logoText: { fontSize: "16px", fontWeight: "700", fontFamily: "var(--font-display)", color: "var(--text-primary)" },
  betaBadge: {
    fontSize: "10px", fontWeight: "600", letterSpacing: "0.08em", textTransform: "uppercase",
    color: "var(--text-muted)", background: "var(--bg-surface)", border: "1px solid var(--border)",
    padding: "2px 8px", borderRadius: "99px",
  },
  headline: {
    fontSize: "clamp(28px, 5vw, 40px)", fontWeight: "800", fontFamily: "var(--font-display)",
    color: "var(--text-primary)", lineHeight: 1.15, letterSpacing: "-0.02em",
  },
  headlineAccent: { color: "var(--accent)", fontStyle: "normal" },
  tagline: { fontSize: "15px", color: "var(--text-secondary)", lineHeight: 1.7, maxWidth: "440px" },
  card: {
    background: "var(--bg-card)", borderRadius: "20px",
    border: "1px solid var(--border)", padding: "32px",
  },
  error: {
    marginBottom: "20px", padding: "12px 16px",
    background: "rgba(226,75,74,0.1)", border: "1px solid rgba(226,75,74,0.3)",
    borderRadius: "10px", fontSize: "13px", color: "#f09595", lineHeight: 1.5,
  },
  footer: {
    display: "flex", gap: "10px", fontSize: "12px",
    color: "var(--text-muted)", flexWrap: "wrap",
  },
  code: {
    fontFamily: "monospace", fontSize: "11px",
    background: "var(--bg-surface)", padding: "1px 6px",
    borderRadius: "4px", border: "1px solid var(--border)",
  },
};