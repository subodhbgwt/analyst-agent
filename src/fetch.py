"""Pulls company info and yearly financials from Yahoo Finance into company.json."""
import json
import sys
from pathlib import Path

import yfinance as yf


def _row(df, *names):
    """Return the first matching row from a yfinance statement as {year: value}."""
    for name in names:
        if name in df.index:
            s = df.loc[name].dropna()
            return {str(k.year): float(v) for k, v in s.items()}
    return {}


def fetch(ticker: str) -> dict:
    t = yf.Ticker(ticker)
    info = t.info
    inc = t.income_stmt
    bs = t.balance_sheet
    cf = t.cashflow

    data = {
        "ticker": ticker,
        "name": info.get("longName") or ticker,
        "currency": info.get("financialCurrency"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "country": info.get("country"),
        "employees": info.get("fullTimeEmployees"),
        "description": info.get("longBusinessSummary"),
        "market_cap": info.get("marketCap"),
        "enterprise_value": info.get("enterpriseValue"),
        "shares_out": info.get("sharesOutstanding"),
        "price": info.get("currentPrice"),
        "ev_ebitda": info.get("enterpriseToEbitda"),
        "pe_trailing": info.get("trailingPE"),
        "financials": {
            "revenue": _row(inc, "Total Revenue"),
            "ebitda": _row(inc, "Normalized EBITDA", "EBITDA"),
            "ebit": _row(inc, "EBIT", "Operating Income"),
            "net_income": _row(inc, "Net Income"),
            "net_debt": _row(bs, "Net Debt"),
            "fcf": _row(cf, "Free Cash Flow"),
            "capex": _row(cf, "Capital Expenditure"),
        },
    }
    return data


if __name__ == "__main__":
    ticker = sys.argv[1]
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("company.json")
    data = fetch(ticker)
    out.write_text(json.dumps(data, indent=2), encoding="utf-8")
    f = data["financials"]
    years = sorted(f["revenue"])
    print(f"{data['name']} ({ticker}), {data['currency']}")
    print(f"years: {years}")
    print(f"written to {out}")
