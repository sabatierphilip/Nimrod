import feedparser


class NewsService:
    feeds = ["https://finance.yahoo.com/news/rssindex", "https://feeds.marketwatch.com/marketwatch/topstories/"]

    def latest(self) -> list[dict[str, str]]:
        seen: set[str] = set()
        articles: list[dict[str, str]] = []
        for feed in self.feeds:
            parsed = feedparser.parse(feed)
            for entry in parsed.entries[:10]:
                title = entry.get("title", "Market update")
                if title in seen:
                    continue
                seen.add(title)
                sentiment = "Bullish" if any(word in title.lower() for word in ["gain", "rally", "rise"]) else "Bearish" if any(word in title.lower() for word in ["fall", "drop", "risk"]) else "Neutral"
                articles.append({"title": title, "url": entry.get("link", ""), "sentiment": sentiment})
        return articles
