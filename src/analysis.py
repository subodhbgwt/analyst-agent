"""Derive growth, margins and a quick two-method valuation from fetched financials."""
import json
import sys
from pathlib import Path


def series(d: dict, years: list) -> list:
    return [d.get(y) for y in years]


def analyze(company: dict, wacc: float = 0.085, tgr: float = 0.02,
            fade_years: int = 5, tax: float = 0.22) -> dict:
    f = company["financials"]
    years = sorted(f["revenue"])
    rev = series(f["revenue"], years)
    ebitda = series(f["ebitda"], years)
    ni = series(f["net_income"], years)
    fcf = series(f["fcf"], years)

    growth = [None] + [
        (rev[i] / rev[i - 1] - 1) if rev[i - 1] else None for i in range(1, len(rev))
    ]
    margins = [
        (e / r) if (e is not None and r) else None for e, r in zip(ebitda, rev)
    ]

    # Mini-DCF on last reported FCF: growth fades linearly from recent
    # revenue CAGR (capped at 10%) down to the terminal rate.
    dcf = None
    fcf_clean = [x for x in fcf if x is not None]
    if fcf_clean and rev[0] and rev[-1]:
        n = len(rev) - 1
        cagr = (rev[-1] / rev[0]) ** (1 / n) - 1 if n > 0 else tgr
        g0 = max(min(cagr, 0.10), tgr)
        base = fcf_clean[-1]
        pv, cash = 0.0, base
        for yr in range(1, fade_years + 1):
            g = g0 + (tgr - g0) * (yr - 1) / max(fade_years - 1, 1)
            cash *= 1 + g
            pv += cash / (1 + wacc) ** yr
        tv = cash * (1 + tgr) / (wacc - tgr)
        pv_tv = tv / (1 + wacc) ** fade_years
        implied_ev = pv + pv_tv
        dcf = {
            "wacc": wacc, "tgr": tgr, "start_growth": g0,
            "pv_fcf": pv, "pv_tv": pv_tv, "implied_ev": implied_ev,
            "actual_ev": company.get("enterprise_value"),
            "upside": (implied_ev / company["enterprise_value"] - 1)
                      if company.get("enterprise_value") else None,
        }

    return {
        "years": years,
        "revenue": rev,
        "revenue_growth": growth,
        "ebitda": ebitda,
        "ebitda_margin": margins,
        "net_income": ni,
        "fcf": fcf,
        "ev_ebitda": company.get("ev_ebitda"),
        "pe": company.get("pe_trailing"),
        "dcf": dcf,
    }


if __name__ == "__main__":
    src = Path(sys.argv[1] if len(sys.argv) > 1 else "company.json")
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("analysis.json")
    company = json.loads(src.read_text(encoding="utf-8"))
    result = analyze(company)
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    if result["dcf"]:
        d = result["dcf"]
        print(f"implied EV {d['implied_ev']/1e9:.1f}bn vs actual {d['actual_ev']/1e9:.1f}bn "
              f"({d['upside']:+.0%}) at {d['wacc']:.1%} WACC / {d['tgr']:.1%} TGR")
    print(f"written to {out}")
