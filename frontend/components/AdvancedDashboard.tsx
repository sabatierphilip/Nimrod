const widgets = ["Watchlist", "Portfolio", "Market Heatmap", "Sector Performance", "Volume Leaders", "Momentum Leaders", "52 Week High/Low", "Upcoming Earnings", "Economic Calendar", "News Panel", "AI Chat", "Trade Journal", "Paper Trading", "Backtesting"];

export function AdvancedDashboard() {
  return <section className="advanced"><div className="sectionHeader"><span className="eyebrow">Advanced mode</span><h2>Professional research dashboard</h2></div><div className="widgetGrid">{widgets.map((widget) => <div className="glass widget" key={widget}><h3>{widget}</h3><p>Modular panel ready for live deterministic analytics, user state, and explainable AI commentary.</p></div>)}</div></section>;
}
