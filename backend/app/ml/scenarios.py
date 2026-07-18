from dataclasses import dataclass


@dataclass(frozen=True)
class MarketScenario:
    name: str
    start_date: str
    end_date: str
    description: str


DEFAULT_MARKET_SCENARIOS: list[MarketScenario] = [
    MarketScenario("COVID Crash", "2020-02-03", "2020-03-23", "High-volatility crash regime."),
    MarketScenario("Recovery Period", "2020-03-24", "2020-08-31", "Post-crash recovery regime."),
    MarketScenario("High Inflation", "2022-01-03", "2022-10-14", "Inflation and rate-hike pressure."),
    MarketScenario("Bull Market", "2023-01-03", "2023-12-29", "Broad upside trend scenario."),
    MarketScenario("Bear Market", "2022-01-03", "2022-12-30", "Broad downside trend scenario."),
    MarketScenario("Sideways Market", "2015-01-02", "2015-12-31", "Range-bound index behavior."),
    MarketScenario("Low Volatility", "2017-01-03", "2017-12-29", "Compressed volatility regime."),
    MarketScenario("High Volatility", "2020-01-02", "2020-06-30", "Elevated realized volatility regime."),
    MarketScenario("Strong Trending Market", "2021-01-04", "2021-12-31", "Persistent trend-following regime."),
    MarketScenario("Range Bound Market", "2018-01-02", "2018-12-31", "Choppy range-bound regime."),
    MarketScenario("Sector Rotation", "2021-09-01", "2022-03-31", "Leadership transition across sectors."),
    MarketScenario("Earnings Season", "2023-10-01", "2023-11-15", "Event-heavy reporting window."),
]
