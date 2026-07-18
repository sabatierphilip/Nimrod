"use client";

import { useState } from "react";
import { MLTrainingResponse, postMLTraining } from "@/lib/api";
import { getGroqKey } from "@/lib/secureStore";

export function MLExperiment() {
  const [result, setResult] = useState<MLTrainingResponse | null>(null);
  const [error, setError] = useState("");
  async function submit(formData: FormData) {
    setError("");
    try {
      const groqKey = await getGroqKey();
      const response = await postMLTraining({
        tickers: [String(formData.get("ticker") || "AAPL")],
        start_date: String(formData.get("start") || "2020-01-01"),
        end_date: String(formData.get("end") || "2024-12-31"),
        prediction_horizon: Number(formData.get("horizon") || 1),
        enabled_models: ["random_forest", "logistic_regression", "gradient_boosting", "extra_trees", "decision_tree"],
        include_llm_explanation: Boolean(groqKey),
        groq_api_key: groqKey,
      });
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "ML experiment failed.");
    }
  }
  return <section className="glass"><div className="sectionHeader"><span className="eyebrow">ML lab</span><h2>Explainable experiments</h2></div><form action={submit} className="gridForm"><input name="ticker" placeholder="Ticker" defaultValue="AAPL" /><input name="start" type="date" defaultValue="2020-01-01" /><input name="end" type="date" defaultValue="2024-12-31" /><select name="horizon"><option value="1">1 day horizon</option><option value="3">3 day horizon</option><option value="5">5 day horizon</option><option value="10">10 day horizon</option><option value="20">20 day horizon</option></select><button>Run ML research</button></form>{error && <p className="error">{error}</p>}{result && <article className="card wide"><h3>ML explanation</h3><p>{result.llm_explanation}</p><p>Models: {result.trained_models.join(", ") || "none"}</p><small>Skipped: {Object.keys(result.skipped_models).length} · Experimental, uncertain, and not financial advice.</small></article>}</section>;
}
