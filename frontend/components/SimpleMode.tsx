"use client";

import { useState } from "react";
import { postSimpleMode, Recommendation } from "@/lib/api";

export function SimpleMode() {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [error, setError] = useState("");
  async function submit(formData: FormData) {
    setError("");
    try {
      const data = await postSimpleMode({ investment_amount: Number(formData.get("amount")), holding_period: formData.get("period"), risk_level: formData.get("risk"), max_stock_price: formData.get("maxPrice") ? Number(formData.get("maxPrice")) : null, preferred_sector: formData.get("sector") || null });
      setRecommendations(data.recommendations);
    } catch (err) { setError(err instanceof Error ? err.message : "Something went wrong."); }
  }
  return <section className="glass"><div className="sectionHeader"><span className="eyebrow">Simple mode</span><h2>Top 5 research opportunities</h2></div><form action={submit} className="gridForm"><input name="amount" type="number" placeholder="Investment Amount" required /><select name="period"><option>Intraday</option><option>1 Day</option><option>1 Week</option><option>1 Month</option></select><select name="risk"><option>Conservative</option><option>Moderate</option><option>Aggressive</option></select><input name="maxPrice" type="number" placeholder="Maximum Stock Price (optional)" /><input name="sector" placeholder="Preferred Sector (optional)" /><button>Analyze</button></form>{error && <p className="error">{error}</p>}<div className="cards">{recommendations.map((item) => <article className="card" key={item.symbol}><div><h3>{item.symbol}</h3><p>${item.current_price}</p></div><strong>{item.opportunity_score}/100</strong><p>Confidence: {item.confidence_score}%</p><p>Entry {item.suggested_entry} · Stop {item.suggested_stop_loss} · Target {item.suggested_target}</p><p>{item.ai_explanation}</p><small>{item.risk_summary}</small></article>)}</div></section>;
}
