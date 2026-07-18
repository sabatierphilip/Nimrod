"use client";

import { useEffect, useState } from "react";
import { AdvancedDashboard } from "@/components/AdvancedDashboard";
import { ApiKeyGate } from "@/components/ApiKeyGate";
import { DisclaimerModal } from "@/components/DisclaimerModal";
import { SimpleMode } from "@/components/SimpleMode";
import { MLExperiment } from "@/components/MLExperiment";
import { getGroqKey } from "@/lib/secureStore";

export default function Home() {
  const [accepted, setAccepted] = useState(false);
  const [hasKey, setHasKey] = useState(false);
  useEffect(() => { setAccepted(localStorage.getItem("nimrod_disclaimer") === "accepted"); getGroqKey().then((key) => setHasKey(Boolean(key))); }, []);
  return <main><DisclaimerModal accepted={accepted} onAccept={() => { localStorage.setItem("nimrod_disclaimer", "accepted"); setAccepted(true); }} /><nav><span>Nimrod</span><a>Research, not advice</a></nav><header className="hero"><p className="eyebrow">AI Trading Assistant</p><h1>Modern stock market research with explicit uncertainty and risk analysis.</h1><p>Nimrod ranks opportunities with deterministic indicators and scoring, while Groq is reserved for explanations, news summaries, education, and natural-language filters.</p></header><ApiKeyGate ready={hasKey} onReady={() => setHasKey(true)} /><SimpleMode /><MLExperiment /><AdvancedDashboard /></main>;
}
