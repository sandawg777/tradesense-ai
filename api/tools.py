import yfinance as yf
import numpy as np
import requests
from datetime import datetime
from langchain_core.tools import tool


@tool
def get_stock_price(ticker: str) -> str:
    """Get current stock price and basic info for a ticker symbol like AAPL, TSLA, MSFT."""
    try:
        stock = yf.Ticker(ticker.upper().strip())
        info = stock.info
        hist = stock.history(period="5d")
        if hist.empty:
            return f"No data found for {ticker}"
        current = hist['Close'].iloc[-1]
        prev = hist['Close'].iloc[-2] if len(hist) > 1 else current
        change = ((current - prev) / prev) * 100
        return f"""
Stock: {ticker.upper()}
Current Price: ${current:.2f}
Change: {change:+.2f}%
52W High: ${info.get('fiftyTwoWeekHigh', 'N/A')}
52W Low: ${info.get('fiftyTwoWeekLow', 'N/A')}
Market Cap: ${info.get('marketCap', 0)/1e9:.2f}B
P/E Ratio: {info.get('trailingPE', 'N/A')}
Volume: {info.get('volume', 'N/A'):,}
Sector: {info.get('sector', 'N/A')}
"""
    except Exception as e:
        return f"Error fetching {ticker}: {str(e)}"


@tool
def get_technical_indicators(ticker: str) -> str:
    """Calculate technical indicators (RSI, MACD, Moving Averages) for a stock ticker."""
    try:
        stock = yf.Ticker(ticker.upper().strip())
        hist = stock.history(period="6mo")
        if hist.empty or len(hist) < 50:
            return f"Not enough data for {ticker}"
        close = hist['Close']
        delta = close.diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1]
        ma50 = close.rolling(50).mean().iloc[-1]
        ma200 = close.rolling(200).mean().iloc[-1] if len(close) >= 200 else None
        current_price = close.iloc[-1]
        ema12 = close.ewm(span=12).mean()
        ema26 = close.ewm(span=26).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9).mean()
        macd_val = macd.iloc[-1]
        signal_val = signal.iloc[-1]
        ma20 = close.rolling(20).mean()
        std20 = close.rolling(20).std()
        upper_band = (ma20 + 2*std20).iloc[-1]
        lower_band = (ma20 - 2*std20).iloc[-1]
        rsi_signal = "OVERBOUGHT" if current_rsi > 70 else "OVERSOLD" if current_rsi < 30 else "NEUTRAL"
        macd_signal = "BULLISH" if macd_val > signal_val else "BEARISH"
        ma200_str = f"${ma200:.2f}" if ma200 else "N/A"
        cross_status = "GOLDEN CROSS" if ma200 and ma50 > ma200 else "DEATH CROSS" if ma200 else "N/A"
        return f"""
Technical Analysis: {ticker.upper()}
Current Price: ${current_price:.2f}
RSI (14): {current_rsi:.1f} -> {rsi_signal}
MACD: {macd_val:.3f} | Signal: {signal_val:.3f} -> {macd_signal}
50-Day MA: ${ma50:.2f} -> Price is {'above' if current_price > ma50 else 'below'} MA50
200-Day MA: {ma200_str} -> {cross_status}
Bollinger Bands: Upper ${upper_band:.2f} | Lower ${lower_band:.2f}
"""
    except Exception as e:
        return f"Error calculating indicators for {ticker}: {str(e)}"


@tool
def get_fundamental_data(ticker: str) -> str:
    """Get fundamental financial data for a stock - earnings, revenue, ratios."""
    try:
        stock = yf.Ticker(ticker.upper().strip())
        info = stock.info
        return f"""
Fundamental Analysis: {ticker.upper()}
Company: {info.get('longName', 'N/A')}
Sector: {info.get('sector', 'N/A')}
Industry: {info.get('industry', 'N/A')}
P/E Ratio: {info.get('trailingPE', 'N/A')}
Forward P/E: {info.get('forwardPE', 'N/A')}
P/B Ratio: {info.get('priceToBook', 'N/A')}
P/S Ratio: {info.get('priceToSalesTrailing12Months', 'N/A')}
Revenue: ${info.get('totalRevenue', 0)/1e9:.2f}B
Gross Margin: {info.get('grossMargins', 0)*100:.1f}%
Operating Margin: {info.get('operatingMargins', 0)*100:.1f}%
EPS: ${info.get('trailingEps', 'N/A')}
Revenue Growth: {info.get('revenueGrowth', 0)*100:.1f}%
Earnings Growth: {info.get('earningsGrowth', 0)*100:.1f}%
Debt/Equity: {info.get('debtToEquity', 'N/A')}
Current Ratio: {info.get('currentRatio', 'N/A')}
Free Cash Flow: ${info.get('freeCashflow', 0)/1e9:.2f}B
Dividend Yield: {info.get('dividendYield', 0)*100:.2f}%
Beta: {info.get('beta', 'N/A')}
"""
    except Exception as e:
        return f"Error fetching fundamentals for {ticker}: {str(e)}"


@tool
def search_trading_knowledge(query: str) -> str:
    """Search the trading knowledge base for indicators, strategies, and concepts."""
    try:
        from langchain_huggingface import HuggingFaceEmbeddings
        import faiss
        with open('data/knowledge.txt', 'r') as f:
            chunks = [line.strip() for line in f.readlines() if line.strip()]
        model = HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')
        embeddings = np.array(model.embed_documents(chunks)).astype(np.float32)
        index = faiss.IndexFlatL2(embeddings.shape[1])
        index.add(embeddings)
        query_vec = np.array([model.embed_query(query)]).astype(np.float32)
        _, indices = index.search(query_vec, 3)
        return "\n".join([chunks[i] for i in indices[0]])
    except Exception as e:
        return f"Knowledge search error: {str(e)}"


@tool
def get_market_news(query: str = "stock market") -> str:
    """Get current financial news. Use for understanding what's happening in the market RIGHT NOW."""
    try:
        url = "https://query2.finance.yahoo.com/v1/finance/search"
        params = {"q": query, "newsCount": 10, "quotesCount": 0}
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, params=params, headers=headers, timeout=10)
        data = response.json()
        news_items = data.get("news", [])[:8]
        if not news_items:
            return f"No recent news found for: {query}"
        result = f"Recent news for '{query}':\n\n"
        for item in news_items:
            title = item.get("title", "")
            publisher = item.get("publisher", "")
            timestamp = item.get("providerPublishTime", 0)
            date = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d") if timestamp else "recent"
            result += f"- [{date}] {publisher}: {title}\n"
        return result
    except Exception as e:
        return f"News fetch error: {str(e)}"


@tool
def get_sector_performance() -> str:
    """Get TODAY's actual sector performance to identify hot sectors RIGHT NOW."""
    try:
        sector_etfs = {
            "Technology": "XLK", "Energy": "XLE", "Financials": "XLF",
            "Healthcare": "XLV", "Industrials": "XLI", "Consumer Discretionary": "XLY",
            "Consumer Staples": "XLP", "Utilities": "XLU", "Real Estate": "XLRE",
            "Materials": "XLB", "Communications": "XLC", "Semiconductors": "SOXX",
            "AI/Robotics": "BOTZ", "Cybersecurity": "CIBR", "Clean Energy": "ICLN",
            "Biotech": "XBI", "Cloud": "SKYY", "Defense": "ITA",
            "Uranium/Nuclear": "URA", "Crypto-related": "BLOK"
        }
        results = []
        for sector, ticker in sector_etfs.items():
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="1mo")
                if hist.empty:
                    continue
                current = hist['Close'].iloc[-1]
                week_ago = hist['Close'].iloc[-5] if len(hist) >= 5 else hist['Close'].iloc[0]
                month_ago = hist['Close'].iloc[0]
                week_change = ((current - week_ago) / week_ago) * 100
                month_change = ((current - month_ago) / month_ago) * 100
                results.append({
                    "sector": sector, "ticker": ticker,
                    "week": week_change, "month": month_change
                })
            except:
                continue
        if not results:
            return "Could not fetch sector data"
        results.sort(key=lambda x: x["month"], reverse=True)
        output = "LIVE SECTOR PERFORMANCE\n"
        output += "=" * 55 + "\n"
        output += f"{'Sector':<25}{'1W':>10}{'1M':>10}\n"
        output += "-" * 55 + "\n"
        output += "\nTOP PERFORMERS (last month):\n"
        for s in results[:5]:
            output += f"{s['sector']:<25}{s['week']:>+9.2f}%{s['month']:>+9.2f}%\n"
        output += "\nWORST PERFORMERS (last month):\n"
        for s in results[-5:]:
            output += f"{s['sector']:<25}{s['week']:>+9.2f}%{s['month']:>+9.2f}%\n"
        return output
    except Exception as e:
        return f"Sector performance error: {str(e)}"


@tool
def screen_stocks(criteria: str) -> str:
    """Screen stocks dynamically by criteria. Examples: 'small cap gainers', 'growth technology', 'most active', 'undervalued'. Returns LIVE stocks matching criteria."""
    try:
        url = "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved"
        headers = {"User-Agent": "Mozilla/5.0"}
        criteria_lower = criteria.lower()
        if "small cap" in criteria_lower:
            screener_id = "small_cap_gainers"
        elif "growth" in criteria_lower:
            screener_id = "growth_technology_stocks"
        elif "undervalued" in criteria_lower or "value" in criteria_lower:
            screener_id = "undervalued_growth_stocks"
        elif "active" in criteria_lower or "volume" in criteria_lower:
            screener_id = "most_actives"
        else:
            screener_id = "day_gainers"
        params = {"scrIds": screener_id, "count": 25}
        response = requests.get(url, params=params, headers=headers, timeout=10)
        data = response.json()
        quotes = data.get("finance", {}).get("result", [{}])[0].get("quotes", [])
        if not quotes:
            return "Screener returned no results."
        sector_keywords = {
            "semiconductor": ["semiconductor", "chip"],
            "tech": ["technology", "software"],
            "biotech": ["biotech", "pharmaceutical"],
            "energy": ["energy", "oil", "gas"],
            "financial": ["financial", "bank"],
            "healthcare": ["healthcare", "medical"]
        }
        sector_filter = None
        for key, keywords in sector_keywords.items():
            if key in criteria_lower:
                sector_filter = keywords
                break
        results = []
        for q in quotes:
            sector = (q.get("sector") or "").lower()
            if sector_filter and not any(k in sector for k in sector_filter):
                continue
            ticker = q.get("symbol", "")
            name = q.get("shortName", q.get("longName", ""))[:30]
            price = q.get("regularMarketPrice", 0)
            change = q.get("regularMarketChangePercent", 0)
            market_cap = q.get("marketCap", 0) / 1e9 if q.get("marketCap") else 0
            if "small cap" in criteria_lower and market_cap > 2:
                continue
            if "mid cap" in criteria_lower and (market_cap < 2 or market_cap > 10):
                continue
            results.append({
                "ticker": ticker, "name": name, "price": price,
                "change": change, "market_cap": market_cap
            })
        if not results:
            return f"No stocks matched '{criteria}'."
        results.sort(key=lambda x: x["change"], reverse=True)
        output = f"LIVE STOCK SCREEN: {criteria}\n"
        output += "=" * 75 + "\n"
        output += f"{'Ticker':<8}{'Name':<32}{'Price':>10}{'Day %':>10}{'MktCap':>12}\n"
        output += "-" * 75 + "\n"
        for r in results[:15]:
            mc = f"${r['market_cap']:.2f}B" if r['market_cap'] else "N/A"
            output += f"{r['ticker']:<8}{r['name']:<32}${r['price']:>8.2f}{r['change']:>+9.2f}%{mc:>12}\n"
        return output
    except Exception as e:
        return f"Screener error: {str(e)}"
