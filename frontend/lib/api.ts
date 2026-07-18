export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export type Recommendation = {
  symbol: string;
  company_name: string;
  current_price: number;
  opportunity_score: number;
  confidence_score: number;
  suggested_entry: number;
  suggested_stop_loss: number;
  suggested_target: number;
  expected_holding_time: string;
  ai_explanation: string;
  risk_summary: string;
};

export async function postSimpleMode(payload: Record<string, unknown>): Promise<{ disclaimer: string; recommendations: Recommendation[] }> {
  const response = await fetch(`${API_BASE_URL}/simple`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
  if (!response.ok) throw new Error("Unable to load opportunities. Nimrod will retry when data providers recover.");
  return response.json();
}

export type MLTrainingResponse = {
  disclaimer: string;
  trained_models: string[];
  skipped_models: Record<string, string>;
  validation_scores: Record<string, number>;
  feature_importance: Array<{ feature: string; importance: number }>;
  reproducibility: Record<string, unknown>;
  llm_explanation: string;
};

export async function postMLTraining(payload: Record<string, unknown>): Promise<MLTrainingResponse> {
  const response = await fetch(`${API_BASE_URL}/ml/train`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
  if (!response.ok) throw new Error("Unable to run ML experiment. Check backend dependencies and try again.");
  return response.json();
}
