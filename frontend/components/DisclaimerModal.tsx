"use client";

export function DisclaimerModal({ accepted, onAccept }: { accepted: boolean; onAccept: () => void }) {
  if (accepted) return null;
  return <div className="modalBackdrop"><div className="modal"><p className="eyebrow">Required disclaimer</p><h2>Market research only</h2><p>This software provides market research and educational analysis only. It does not guarantee profits and should not be considered financial advice.</p><button onClick={onAccept}>I understand</button></div></div>;
}
