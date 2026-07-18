SYSTEM_PROMPT = """You are Nimrod, an AI market research analyst. Never claim certainty, never guarantee profits, and never invent market data. Explain uncertainty, risks, and educational context only. Technical indicators and scores are provided by deterministic services."""


class GroqLLMService:
    endpoint = "https://api.groq.com/openai/v1/chat/completions"

    async def complete(self, api_key: str, model: str, user_message: str, context: str = "") -> str:
        import httpx

        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {"model": model, "messages": [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": f"Context: {context}\n\nRequest: {user_message}"}], "temperature": 0.3}
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(self.endpoint, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]

    def interpret_filters(self, message: str) -> dict[str, str | float | int | None]:
        lowered = message.lower()
        filters: dict[str, str | float | int | None] = {}
        if "under" in lowered:
            parts = lowered.replace("₹", " ").replace("$", " ").split()
            numbers = [float(part) for part in parts if part.replace(".", "", 1).isdigit()]
            if numbers:
                filters["max_stock_price"] = numbers[-1]
        if "momentum" in lowered:
            filters["strategy"] = "momentum"
        if "lowest risk" in lowered or "low risk" in lowered:
            filters["risk_level"] = "conservative"
        return filters
