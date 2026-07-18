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


export type TradeRecommendation = {
  rank: number; symbol: string; buy_price: number; expected_return: number; probability: number; confidence: string; risk_score: number; liquidity_score: number; momentum_score: number; trend_score: number; volatility_score: number; final_opportunity_score: number; quantity: number; allocated_capital: number; reasons: string[];
};
export type RecommendResponse = { disclaimer: string; mode: string; as_of: string; recommendations: TradeRecommendation[]; portfolio_metrics: { expected_portfolio_return: number; risk_rating: string; diversification: string; suggested_allocation: Record<string, number>; total_allocated: number; cash_remaining: number; estimated_costs: number; actual_return: number | null; profit_loss: number | null; win_rate: number | null; benchmark_return: number | null; drawdown: number | null; equity_curve: Array<Record<string, string | number>>; }; trade_log: Array<Record<string, string | number>>; model_confidence: number; reasoning: string[]; warnings: string[]; };
export async function postRecommendations(payload: Record<string, unknown>): Promise<RecommendResponse> {
  const response = await fetch(`${API_BASE_URL}/recommend`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
  if (!response.ok) throw new Error("Unable to generate ML recommendations. Check dates, capital, and backend market data.");
  return response.json();
}
