from app.models.trading import RiskPlan


class RiskManagementService:
    def build_plan(self, capital: float, entry: float, stop_loss: float, target: float, risk_percent: float = 1.0) -> RiskPlan:
        max_risk = capital * risk_percent / 100
        per_share_risk = max(entry - stop_loss, 0.01)
        position_size = int(max_risk // per_share_risk)
        potential_loss = round(position_size * per_share_risk, 2)
        potential_gain = round(position_size * max(target - entry, 0), 2)
        ratio = round((target - entry) / per_share_risk, 2)
        return RiskPlan(capital=capital, max_risk=max_risk, position_size=position_size, risk_reward_ratio=ratio, stop_loss=stop_loss, target_price=target, potential_gain=potential_gain, potential_loss=potential_loss)
