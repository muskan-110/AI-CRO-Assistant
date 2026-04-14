/**
 * Formats the raw API personalization result into UI-friendly shape.
 */
export function formatPersonalizationResult(raw) {
  return {
    html: raw.personalizedHtml || "",
    changes: Array.isArray(raw.changes) ? raw.changes : [],
    score: typeof raw.score === "number" ? raw.score : null,
  };
}

/**
 * Formats ad analysis into readable summary lines.
 */
export function formatAdAnalysis(analysis) {
  if (!analysis) return [];
  return [
    { label: "Headline", value: analysis.headline },
    { label: "CTA", value: analysis.cta },
    { label: "Theme", value: analysis.theme },
    { label: "Audience", value: analysis.audience },
    { label: "Tone", value: analysis.tone },
  ].filter((item) => item.value);
}

/**
 * Truncates a URL for display.
 */
export function truncateUrl(url, maxLength = 48) {
  try {
    const { hostname, pathname } = new URL(url);
    const short = hostname + pathname;
    return short.length > maxLength ? short.slice(0, maxLength) + "…" : short;
  } catch {
    return url.slice(0, maxLength);
  }
}