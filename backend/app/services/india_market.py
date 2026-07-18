from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time


NSE_UNIVERSE = [
    "BEL.NS", "INFY.NS", "HAL.NS", "TCS.NS", "LTIM.NS", "TATAMOTORS.NS", "ITC.NS", "SBIN.NS",
    "ONGC.NS", "NTPC.NS", "POWERGRID.NS", "COALINDIA.NS", "WIPRO.NS", "HCLTECH.NS", "ICICIBANK.NS",
    "HDFCBANK.NS", "AXISBANK.NS", "RELIANCE.NS", "BHARTIARTL.NS", "MARUTI.NS", "SUNPHARMA.NS",
    "NIFTYBEES.NS", "BANKBEES.NS", "JUNIORBEES.NS",
]

NSE_BENCHMARKS = {"NSE": "^NSEI", "NIFTY 50": "^NSEI", "BANK NIFTY": "^NSEBANK", "NIFTY NEXT 50": "JUNIORBEES.NS", "NIFTY MIDCAP": "MID150BEES.NS"}

INDIAN_MARKET_HOLIDAYS_2025_2026 = {
    date(2025, 1, 26), date(2025, 2, 26), date(2025, 3, 14), date(2025, 3, 31), date(2025, 4, 10),
    date(2025, 4, 14), date(2025, 4, 18), date(2025, 5, 1), date(2025, 8, 15), date(2025, 8, 27),
    date(2025, 10, 2), date(2025, 10, 21), date(2025, 10, 22), date(2025, 11, 5), date(2025, 12, 25),
    date(2026, 1, 26), date(2026, 3, 3), date(2026, 3, 21), date(2026, 3, 31), date(2026, 4, 3),
    date(2026, 4, 14), date(2026, 5, 1), date(2026, 8, 15), date(2026, 10, 2), date(2026, 10, 20),
    date(2026, 11, 9), date(2026, 12, 25),
}


def is_indian_trading_day(value: date) -> bool:
    return value.weekday() < 5 and value not in INDIAN_MARKET_HOLIDAYS_2025_2026


def market_cutoff(value: date) -> datetime:
    return datetime.combine(value, time(15, 30))


@dataclass(frozen=True)
class BrokerageBreakdown:
    brokerage: float
    stt: float
    exchange_transaction: float
    sebi: float
    gst: float
    stamp_duty: float
    dp_charges: float

    @property
    def total(self) -> float:
        return round(self.brokerage + self.stt + self.exchange_transaction + self.sebi + self.gst + self.stamp_duty + self.dp_charges, 2)


class IndianBrokerageCalculator:
    """Conservative delivery-equity cost calculator for Indian retail simulations."""

    def estimate_delivery(self, buy_value: float, sell_value: float, brokerage_rate: float = 0.0) -> BrokerageBreakdown:
        turnover = buy_value + sell_value
        brokerage = min(turnover * brokerage_rate, 40.0) if brokerage_rate else 0.0
        stt = sell_value * 0.001
        exchange = turnover * 0.0000322
        sebi = turnover * 0.000001
        gst = (brokerage + exchange + sebi) * 0.18
        stamp = buy_value * 0.00015
        dp = 15.93 if sell_value > 0 else 0.0
        return BrokerageBreakdown(round(brokerage, 2), round(stt, 2), round(exchange, 2), round(sebi, 2), round(gst, 2), round(stamp, 2), round(dp, 2))
