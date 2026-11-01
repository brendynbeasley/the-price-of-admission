"""Costco's membership plan, year by year, and the extension: Armstrong's small-increase argument on its fee.

Part 1 reads every Costco 10-K from fiscal 2005 to 2026 for the facts its financial data does not carry (paid
members, cardholders, Executive members and their share of sales, renewal rates, fee levels) and joins them
to the income statement from the XBRL filed with each report. It then builds the two-line menu in the latest
year and sets paid memberships against the number of US households (FRED series TTLHH).

Part 2 is the extension. Armstrong's exclusion argument says that raising the entry price by a small amount
gains that amount from nearly every buyer and loses only the few at the very bottom. Costco raised its US
Gold Star fee by $5 four times (taking effect in fiscal 2006, 2012, 2017 and 2025). For each increase the
script sets the extra fee revenue Costco reported for the first full year afterward against the most the
increase could have cost in lost members: any fall in the renewal rate from the year before to the lower of
the two years after is treated as members driven out, applied to every paid member, and charged the fee
plus the margin Costco earns on an average member's purchases. It then regresses the year-to-year change in
the US and Canada renewal rate on an increase-year indicator, with HC1 standard errors and a permutation test.

Uses the download and XBRL helpers in src/warehouse_tariffs.py (documents are cached in data/raw/sec/).

Usage (from the repository root):
    python src/costco_membership.py
Writes results/costco_history.csv, costco_menu.csv, costco_exclusion.csv, fee_increases.csv,
renewal_test.csv, costco_tariff.png and renewal_rates.png.
"""

import re
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker
import numpy as np
import pandas as pd
import statsmodels.api as sm

sys.path.insert(0, str(Path(__file__).resolve().parent))   # so the import works under python -I as well
from warehouse_tariffs import (OUT, RAW, filing_text, fred_series, income_statements,  # noqa: E402
                               load_filings, tariff_measures)

CIK = 909832
FEE_INCREASE_YEARS = [2006, 2012, 2017, 2025]   # fiscal years in which a US fee increase took effect; the
                                                # matching 10-K sentences are printed below as a check
FEE_BEFORE_2006 = 45.0     # US Gold Star fee before the May 2006 increase ("increased annual membership fees by $5",
                           # Costco fiscal 2006 10-K, which gives the new individual fee as $50)
FEE_STEP = 5.0             # each of the four US increases was $5 (fiscal 2006, 2012, 2017 and 2025 10-Ks)
EXEC_REWARD_RATE = 0.02    # Executive reward, "generally 2% on qualified purchases" (Costco fiscal 2026 10-K)

# Where Costco reported the revenue effect of each increase for the first full year after it:
# increase year -> (report fiscal year, pattern, kind). "amount" patterns capture $ millions directly;
# "share" patterns capture the percentage of that year's growth in membership fee revenue.
IMPACT_SOURCES = {
    2012: (2013, r"fee increases had a positive impact on membership fee.{0,300}?revenues of approximately \$(\d+) and", "amount"),
    2017: (2018, r"fee increases had a positive impact of approximately \$(\d+) in fiscal 2018", "amount"),
    2025: (2025, r"fee income increase accounted for approximately (\d+)% of membership income growth during 2025", "share"),
}
PERMUTATIONS = 100_000          # draws for the permutation test
SEED = 2017


def reported_gain(hist, filings, increase_year):
    if increase_year not in IMPACT_SOURCES:
        return np.nan, ""
    report_year, pattern, kind = IMPACT_SOURCES[increase_year]
    acc = filings.loc[filings.fiscal_year == report_year, "accession"].iloc[0]
    text = filing_text(CIK, acc)
    m = re.search(pattern, text, re.I | re.S)
    if not m:
        print(f"  no impact sentence found in the fiscal {report_year} 10-K")
        return np.nan, ""
    value = float(m.group(1))
    if kind == "share":
        growth = (hist.fees[report_year] - hist.fees[report_year - 1]) / 1e6
        value = value / 100 * growth
    sentence = re.sub(r"\s*\d+ Table of Contents .*?\(Continued\)\s*", " ", m.group(0))   # page-break header
    return value, sentence[:200]


def permutation_test(changes, event_years):
    """Difference in mean renewal-rate change, event years minus other years, and its two-sided p-value."""
    d = changes.dropna()
    is_event = d.index.isin(event_years)
    observed = d[is_event].mean() - d[~is_event].mean()
    rng = np.random.default_rng(SEED)
    draws = np.empty(PERMUTATIONS)
    for i in range(PERMUTATIONS):
        flip = rng.permutation(is_event)
        draws[i] = d[flip].mean() - d[~flip].mean()
    p = (np.abs(draws) >= abs(observed) - 1e-12).mean()
    return observed, p, int(is_event.sum()), int((~is_event).sum())



# ---------------------------------------------------------------- 10-K text


def number(pattern, text):
    m = re.search(pattern, text, re.I)
    return float(m.group(1).replace(",", "")) if m else np.nan


def parse_costco(text):
    """Membership facts from one Costco 10-K. Phrasing changed over the years; the patterns cover the
    variants used from fiscal 2006 to fiscal 2026."""
    us = r"U\.\s?S\.\s?(?:and|&) Canada"
    out = {
        "renewal_us_canada": number(rf"renewal rates?,? (?:was|were|is|are)?\s*(?:approximately |currently )?"
                                    rf"(?:at )?([\d.]+)% in the {us}", text),
        "renewal_worldwide": number(rf"in the {us},? and (?:approximately )?([\d.]+)% (?:on a )?worldwide", text),
        "renewal_unsplit": number(r"renewal rates?[^.%]{0,60}?currently (?:at )?(?:approximately )?([\d.]+)%", text),
        "paid_members_k": number(r"(?:Total paid members|Total paid cardholders|Total primary cardholders|Paid members)(?:\s*\(?\d\)?)?\s+([\d,]{5,})", text),
        "cardholders_k": number(r"Total cardholders\s+([\d,]{5,})", text),
        "exec_share_of_paid_pct": number(r"Executive members represented (?:approximately )?([\d.]+)%(?:, [\d.]+%,? and "
                                         r"[\d.]+%,? respectively,?)? of (?:our )?(?:paid members|primary membership)", text),
        "exec_members_k": number(r"Executive members represented ([\d,]{5,}),", text),
        "exec_members_prior_k": number(r"Executive members represented [\d,]{5,}, ([\d,]{5,}),", text),
        "exec_share_of_sales_pct": number(r"Executive members?.{0,160}?approximately ([\d.]+)% of (?:our )?"
                                          r"(?:worldwide |consolidated |total )?net sales", text),
        "fee_us_gold_star": number(r"annual fee for (?:these )?memberships is \$(\d+) in the U\.\s?S\.", text),
        "exec_upgrade_fee": number(r"Executive.{0,120}?additional annual fee of (?:approximately )?\$(\d+)", text),
    }
    if np.isnan(out["fee_us_gold_star"]):
        out["fee_us_gold_star"] = number(r"(?:Gold Star|Individual) member(?:ship)?s? (?:are also available for |"
                                         r"generally pay )an annual (?:membership )?fee of (?:approximately )?\$(\d+)", text)
    if np.isnan(out["exec_members_k"]) and not np.isnan(out["exec_share_of_paid_pct"]):
        out["exec_members_k"] = out["exec_share_of_paid_pct"] / 100 * out["paid_members_k"]
    increase = re.search(r"[^.]*increased (?:our |the )?(?:U\.\s?S\.\s?and Canada )?annual membership fees?[^.]*\.",
                         text, re.I)
    out["fee_increase_sentence"] = increase.group(0).strip()[:400] if increase else ""
    return out


def costco_tariff_figure(hist):
    d = hist.dropna(subset=["fees_pct_sales"])
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    ax.plot(d.index, d.fees_pct_sales, marker="o", ms=3, color="#3182bd", label="Membership fees")
    ax.plot(d.index, d.merch_margin_pct, marker="o", ms=3, color="#636363",
            label="Margin left on merchandise after operating costs")
    for fy in FEE_INCREASE_YEARS:
        ax.axvline(fy, color="#bbbbbb", lw=0.8, ls="--")
    ax.set_ylabel("Percent of merchandise sales")
    ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
    ax.set_title("Costco's operating profit, split between the door and the aisles", fontsize=10)
    ax.set_ylim(0, max(d.fees_pct_sales.max(), d.merch_margin_pct.max()) * 1.4)
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    ax.text(0.99, 0.02, "dashed lines: fiscal years in which a US fee increase took effect", transform=ax.transAxes,
            ha="right", fontsize=7, color="#666666")
    fig.tight_layout()
    fig.savefig(OUT / "costco_tariff.png", dpi=160)
    plt.close(fig)


def costco_history(filings):
    cf = filings[filings.company == "Costco"].sort_values("fiscal_year")
    text = pd.DataFrame([dict(fiscal_year=f.fiscal_year, **parse_costco(filing_text(CIK, f.accession)))
                         for _, f in cf.iterrows()]).set_index("fiscal_year")
    prior = text.exec_members_prior_k.copy()
    prior.index = prior.index - 1                     # each report also gives the previous year's count
    text["exec_members_k"] = text.exec_members_k.combine_first(prior.reindex(text.index))
    fin = income_statements(cf)
    fin["merch_sales"] = fin.revenue - fin.fees
    hist = text.join(tariff_measures(fin), how="left")
    cpi = fred_series("CPIAUCSL")
    cpi_year = cpi.groupby(cpi.date.dt.year).value.mean()
    hist = hist.rename(columns={"fee_us_gold_star": "fee_us_gold_star_stated"})
    hist["fee_us_gold_star"] = [FEE_BEFORE_2006 + FEE_STEP * sum(y <= fy for y in FEE_INCREASE_YEARS)
                                for fy in hist.index]
    hist["fee_in_2025_dollars"] = hist.fee_us_gold_star * cpi_year[2025] / cpi_year.reindex(hist.index).values
    hist["sales_per_paid_member"] = hist.merch_sales / (hist.paid_members_k * 1e3)
    hist.to_csv(OUT / "costco_history.csv", float_format="%.4f")
    print("\nCostco, by fiscal year:")
    print(hist[["renewal_us_canada", "renewal_worldwide", "renewal_unsplit", "paid_members_k", "exec_members_k",
                "exec_share_of_sales_pct", "fee_us_gold_star", "fees_pct_sales", "merch_margin_pct",
                "fees_share_of_opinc_pct"]].round(2).to_string())
    print("\nFee-increase sentences found in the 10-Ks:")
    for fy, s in hist.fee_increase_sentence.items():
        if s:
            print(f"  {fy}: {s[:240]}")

    # the menu in the latest year: Executive members against everyone else
    ok = hist.dropna(subset=["exec_share_of_sales_pct", "exec_members_k", "merch_sales"])
    fy, last = ok.index[-1], ok.iloc[-1]
    other_k = last.paid_members_k - last.exec_members_k
    upgrade = hist.exec_upgrade_fee.ffill().get(fy, np.nan)
    menu = pd.DataFrame([
        dict(tier="Executive", members_k=last.exec_members_k, share_of_sales_pct=last.exec_share_of_sales_pct,
             sales_per_member=last.merch_sales * last.exec_share_of_sales_pct / 100 / (last.exec_members_k * 1e3)),
        dict(tier="Gold Star and Business", members_k=other_k, share_of_sales_pct=100 - last.exec_share_of_sales_pct,
             sales_per_member=last.merch_sales * (1 - last.exec_share_of_sales_pct / 100) / (other_k * 1e3)),
    ])
    menu.insert(0, "fiscal_year", fy)
    menu["us_fee"] = [last.fee_us_gold_star + upgrade, last.fee_us_gold_star]
    menu["executive_breakeven_spend"] = upgrade / EXEC_REWARD_RATE
    menu.to_csv(OUT / "costco_menu.csv", index=False, float_format="%.2f")
    print(f"\nCostco menu, fiscal {fy}:\n" + menu.round(2).to_string(index=False))

    # who is left out: paid memberships against US households
    hh = fred_series("TTLHH")
    hh_year = hh.groupby(hh.date.dt.year).value.last()
    excl = pd.DataFrame({"paid_members_worldwide_k": hist.paid_members_k,
                         "us_households_k": hh_year.reindex(hist.index)}).dropna()
    excl["max_share_of_us_households_pct"] = 100 * excl.paid_members_worldwide_k / excl.us_households_k
    excl["min_share_without_card_pct"] = 100 - excl.max_share_of_us_households_pct
    excl.to_csv(OUT / "costco_exclusion.csv", float_format="%.2f")
    print("\nCostco paid memberships against US households:\n" + excl.round(1).to_string())

    costco_tariff_figure(hist)
    return hist


def fee_increases(hist, filings):
    # US and Canada rate where reported (fiscal 2011 on); before that Costco gave one company-wide rate
    renewal = hist.renewal_us_canada.combine_first(hist.renewal_unsplit)

    rows = []
    for fy in FEE_INCREASE_YEARS:
        before = renewal.get(fy - 1, np.nan)
        after = np.nanmin([renewal.get(fy, np.nan), renewal.get(fy + 1, np.nan)])
        members_k = hist.paid_members_k.get(fy - 1, np.nan)
        per_member = hist.sales_per_paid_member.get(fy - 1, np.nan) * hist.merch_margin_pct.get(fy - 1, np.nan) / 100
        drop = max(before - after, 0.0)
        lost_k = drop / 100 * members_k
        loss = lost_k * 1e3 * (hist.fee_us_gold_star[fy] + (per_member if not np.isnan(per_member) else 0)) / 1e6
        gain, sentence = reported_gain(hist, filings, fy)
        rows.append(dict(increase_fiscal_year=fy, fee_before=hist.fee_us_gold_star[fy] - FEE_STEP,
                         fee_after=hist.fee_us_gold_star[fy], renewal_year_before=before,
                         renewal_lowest_two_years_after=after, renewal_change=after - before,
                         paid_members_year_before_k=members_k, merch_margin_per_member=per_member,
                         max_members_lost_k=lost_k, max_loss_musd=loss, reported_gain_first_full_year_musd=gain,
                         gain_sentence=sentence))
    out = pd.DataFrame(rows)
    out.to_csv(OUT / "fee_increases.csv", index=False, float_format="%.3f")
    print(out.drop(columns="gain_sentence").round(2).to_string(index=False))
    for _, r in out.iterrows():
        if r.gain_sentence:
            print(f"  {r.increase_fiscal_year}: \"{r.gain_sentence}\"")

    return out


def renewal_test(hist):
    """Year-to-year change in the US and Canada renewal rate regressed on an increase-year indicator."""
    us = hist.renewal_us_canada.dropna()
    changes = us.diff().dropna()
    event = [y for fy in FEE_INCREASE_YEARS for y in (fy, fy + 1)]
    inc = changes.index.isin(event).astype(float)
    fit = sm.OLS(changes.values, sm.add_constant(inc)).fit(cov_type="HC1")
    diff, p, n_event, n_other = permutation_test(changes, event)
    lo, hi = fit.conf_int()[1]
    test = pd.DataFrame([dict(measure="change in US and Canada renewal rate (points)",
                              mean_increase_years=changes[inc == 1].mean(), mean_other_years=changes[inc == 0].mean(),
                              delta_hat=fit.params[1], se_hc1=fit.bse[1], ci95_low=lo, ci95_high=hi,
                              p_hc1=fit.pvalues[1], permutation_p=p, n_increase_years=n_event, n_other_years=n_other,
                              n=len(changes), years=f"{changes.index.min()}-{changes.index.max()}")])
    test.to_csv(OUT / "renewal_test.csv", index=False, float_format="%.4f")
    print("\n" + test.round(3).to_string(index=False))
    return us


def renewal_figure(hist, us):
    fig, ax = plt.subplots(figsize=(7.5, 4.0))
    ww = hist.renewal_worldwide.combine_first(hist.renewal_unsplit).dropna()
    ax.plot(us.index, us, marker="o", ms=3, color="#3182bd", label="US and Canada")
    ax.plot(ww.index, ww, marker="o", ms=3, color="#9e9e9e", label="Worldwide (company-wide rate before 2011)")
    for fy in FEE_INCREASE_YEARS:
        ax.axvline(fy, color="#bbbbbb", lw=0.8, ls="--")
        ax.text(fy, 93.7, f"\\${hist.fee_us_gold_star[fy - 1]:.0f} to \\${hist.fee_us_gold_star[fy]:.0f}",
                ha="center", fontsize=7, color="#555555")
    ax.set_ylim(84, 94.3)
    ax.set_ylabel("Member renewal rate (%)")
    ax.set_title("Costco's renewal rate through four \\$5 fee increases", fontsize=10)
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    fig.tight_layout()
    fig.savefig(OUT / "renewal_rates.png", dpi=160)
    plt.close(fig)




def main():
    OUT.mkdir(exist_ok=True)
    filings = load_filings()
    hist = costco_history(filings)
    fee_increases(hist, filings[filings.company == "Costco"])
    us = renewal_test(hist)
    renewal_figure(hist, us)
    print("\nWrote costco_history.csv, costco_menu.csv, costco_exclusion.csv, fee_increases.csv, renewal_test.csv, "
          "costco_tariff.png and renewal_rates.png")


if __name__ == "__main__":
    main()
