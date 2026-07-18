"use client";

import { useState } from "react";
import { saveGroqKey } from "@/lib/secureStore";

export function ApiKeyGate({ ready, onReady }: { ready: boolean; onReady: () => void }) {
  const [key, setKey] = useState("");
  if (ready) return null;
  return <section className="glass keyGate"><h2>Enter your Groq API Key</h2><p>The key is stored locally only and is sent only to Groq-compatible AI endpoints for explanations and educational chat.</p><input type="password" value={key} onChange={(event) => setKey(event.target.value)} placeholder="gsk_..." /><button onClick={async () => { await saveGroqKey(key); onReady(); }}>Save locally</button></section>;
}
