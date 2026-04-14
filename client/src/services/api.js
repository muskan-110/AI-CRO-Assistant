import axios from "axios";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function analyzeAdCreative(creative) {
  let adCreative = "";
  if (creative.file) {
    adCreative = await convertToBase64(creative.file);
  } else if (creative.url) {
    adCreative = creative.url;
  }

  const res = await axios.post(`${API_BASE}/analyze-ad`, { adCreative });
  return res.data;
}

export async function scrapeLandingPage(url) {
  const res = await axios.post(`${API_BASE}/scrape`, { url });
  return res.data;
}

export async function generatePersonalizedPage({ adAnalysis, pageData, landingUrl }) {
  try {
    const res = await axios.post(`${API_BASE}/generate`, {
      adCreative: adAnalysis,
      landingUrl,
      pageData: pageData || {},
    });
    return res.data;
  } catch (error) {
    // Surface balance errors clearly to the user
    if (error.response?.status === 402) {
      throw new Error(
        "OpenRouter balance is negative. Please top up at https://openrouter.ai/credits and try again."
      );
    }
    throw error;
  }
}

function convertToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result);
    reader.onerror = (err) => reject(err);
  });
}