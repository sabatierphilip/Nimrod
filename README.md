# Nimrod AI Trading Assistant

Nimrod is a modern AI-powered stock market research application. It is designed to act as an AI research analyst, not as a financial advisor.

> This software provides market research and educational analysis only. It does not guarantee profits and should not be considered financial advice.

## Architecture

- `backend/`: FastAPI API with market-data adapters, technical indicators, deterministic scoring, risk tools, news aggregation, journal, paper trading, and backtesting.
- `frontend/`: React + Next.js dashboard with dark glassmorphism UI, simple mode, advanced dashboard, charts, news, AI chat, trade journal, paper trading, and backtesting screens.

## Data Sources

The backend is built around free/public sources, preferring Yahoo Finance, then Alpha Vantage, Finnhub, Financial Modeling Prep, NewsAPI, and RSS feeds. Optional keys are read from `.env` and are never hardcoded.

## LLM Guardrails

Groq is used only for explanations, news summaries, risk explanations, educational responses, portfolio commentary, and natural-language filter conversion. Technical indicators, scores, and market data are calculated by deterministic backend services only.

On first launch, the frontend asks for `Enter your Groq API Key`, encrypts it locally with Web Crypto, and sends it only to backend Groq proxy endpoints when an AI explanation or chat response is requested.

## Quick Start

### Backend

```bash
cd backend
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

Open http://localhost:3000.

## Checks

```bash
cd backend && python -m pytest
cd frontend && npm run lint
```

## Experimental Machine Learning Engine

The backend includes a lightweight in-house ML engine under `backend/app/ml/`. It is independent from the LLM and is intended for objective experimentation only; it must never be interpreted as a guarantee of returns.

Capabilities:

- Deterministic feature engineering for RSI, MACD, EMA/SMA, VWAP, ATR, ADX, OBV, returns, volatility, volume change, support/resistance distance, gaps, 52-week position, relative strength, news sentiment, sector strength, market trend, and volatility index proxies.
- Label generation for next/forward returns, positive return probability, outperforming market, binary direction, and multi-class direction using only the selected horizon.
- Strict data-leakage guardrails: chronological indices, no random K-Fold, horizon overlap checks, and train-only preprocessing through scikit-learn compatible pipelines.
- Time-series validation strategies: expanding window, rolling window, walk-forward, and blocked cross-validation.
- Pluggable model registry for Random Forest, Logistic Regression, Gradient Boosting, Extra Trees, Decision Trees, and optional XGBoost/LightGBM if those packages are installed and enabled.
- Ensemble methods for majority voting, weighted voting, and probability averaging.
- Live-like historical simulation that retrains sequentially using only candles available up to each simulated date.
- Reports with model ranking, feature importance, reproducibility metadata, uncertainty disclaimers, and improvement suggestions.

ML endpoints:

- `GET /ml/scenarios` lists default historical scenarios.
- `POST /ml/train` trains enabled models for a ticker and returns validation, skipped model, feature importance, and reproducibility details.
- `POST /ml/simulate` performs sequential historical simulation with configurable capital, allocations, stop, target, and costs.
