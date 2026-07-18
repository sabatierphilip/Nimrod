"use client";

import { useMemo, useState } from "react";
import { postRecommendations, type RecommendResponse } from "@/lib/api";

export function AITradeFinder() {
  const today = useMemo(() => new Date().toISOString().slice(0, 10), []);
  const tomorrow = useMemo(() => { const d = new Date(); d.setDate(d.getDate() + 1); return d.toISOString().slice(0, 10); }, []);
  const [form, setForm] = useState({ market: "NSE", buy_date: today, sell_date: tomorrow, capital: 100, number_of_stocks: 5, risk_level: "Medium" });
  const [data, setData] = useState<RecommendResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  async function submit() {
    setLoading(true); setError("");
    try { setData(await postRecommendations(form)); } catch (exc) { setError(exc instanceof Error ? exc.message : "Recommendation run failed."); } finally { setLoading(false); }
  }
  function csv() {
    if (!data) return "";
    const header = "Rank,Symbol,Buy Price,Expected Return,Probability,Confidence,Quantity,Allocation";
    const rows = data.recommendations.map((r) => [r.rank, r.symbol, r.buy_price, r.expected_return, r.probability, r.confidence, r.quantity, r.allocated_capital].join(","));
    return [header, ...rows].join("\n");
  }
  return <section className="glass tradeFinder"><div className="sectionHeader"><div><p className="eyebrow">AI Trade Finder</p><h2>India-first ML picks for small portfolios.</h2><p>Choose dates, capital, count, and risk. Nimrod trains deterministic point-in-time models and ranks affordable NSE opportunities.</p></div></div><div className="gridForm"><label>Market<select value={form.market} onChange={(e) => setForm({ ...form, market: e.target.value })}><option>NSE</option><option>NIFTY 50</option><option>NIFTY NEXT 50</option><option>NIFTY MIDCAP</option><option>BANK NIFTY</option></select></label><label>Buy Date<input type="date" value={form.buy_date} onChange={(e) => setForm({ ...form, buy_date: e.target.value })} /></label><label>Sell Date<input type="date" value={form.sell_date} onChange={(e) => setForm({ ...form, sell_date: e.target.value })} /></label><label>Capital (₹)<input type="number" min="1" value={form.capital} onChange={(e) => setForm({ ...form, capital: Number(e.target.value) })} /></label><label>Number of Stocks<input type="number" min="1" max="20" value={form.number_of_stocks} onChange={(e) => setForm({ ...form, number_of_stocks: Number(e.target.value) })} /></label><label>Risk<select value={form.risk_level} onChange={(e) => setForm({ ...form, risk_level: e.target.value })}><option>Low</option><option>Medium</option><option>High</option></select></label><button onClick={submit} disabled={loading}>{loading ? "Training models..." : "Generate Recommendations"}</button></div>{error && <p className="error">{error}</p>}{data && <div className="results"><div className="widgetGrid"><div className="widget"><h3>Portfolio Summary</h3><p>Expected return: <strong>{data.portfolio_metrics.expected_portfolio_return}%</strong></p><p>Risk: {data.portfolio_metrics.risk_rating}</p><p>Costs: ₹{data.portfolio_metrics.estimated_costs}</p></div><div className="widget"><h3>Diversification</h3><p>{data.portfolio_metrics.diversification}</p><p>Cash remaining: ₹{data.portfolio_metrics.cash_remaining}</p></div><div className="widget"><h3>Replay Performance</h3><p>Actual return: {data.portfolio_metrics.actual_return ?? "Live mode"}%</p><p>P/L: ₹{data.portfolio_metrics.profit_loss ?? "—"}</p><p>Win rate: {data.portfolio_metrics.win_rate ?? "—"}%</p></div></div><div className="tableWrap"><table><thead><tr><th>Rank</th><th>Symbol</th><th>Buy Price</th><th>Expected Return</th><th>Probability</th><th>Confidence</th><th>Qty</th><th>Allocation</th></tr></thead><tbody>{data.recommendations.map((r) => <tr key={r.symbol}><td>{r.rank}</td><td>{r.symbol}</td><td>₹{r.buy_price}</td><td>{r.expected_return}%</td><td>{Math.round(r.probability * 100)}%</td><td>{r.confidence}</td><td>{r.quantity}</td><td>₹{r.allocated_capital}</td></tr>)}</tbody></table></div><div className="cards">{data.recommendations.map((r) => <article className="card" key={r.symbol}><div><h3>{r.symbol}</h3><strong>#{r.rank}</strong></div><p>Final opportunity score: {r.final_opportunity_score}</p><ul>{r.reasons.map((reason) => <li key={reason}>{reason}</li>)}</ul></article>)}</div><a className="download" href={`data:text/csv;charset=utf-8,${encodeURIComponent(csv())}`} download="nimrod-recommendations.csv">Download CSV</a><button onClick={submit}>Replay Again</button>{data.warnings.map((warning) => <p className="error" key={warning}>{warning}</p>)}</div>}</section>;
}
