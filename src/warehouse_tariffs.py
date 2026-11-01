"""Armstrong's cost-based tariff on real books: warehouse clubs against retailers that charge no fee.

Armstrong (1996) found that, in the cases he could solve, a multiproduct seller's optimal tariff is cost-based,
and that the seller always prices some low-value buyers out of the market. His later survey describes the
many-product version as an entry fee plus unit prices close to cost, with the fee leaving some buyers out.
Warehouse clubs sell thousands of products on that plan. This script measures each retailer's tariff in
fiscal 2021-2025 from the XBRL financial data filed with its 10-K: markup of sales over the cost of goods,
operating costs per dollar of sales, the margin left on merchandise after those costs, and membership fees
as a share of operating income (clubs: Costco, BJ's, PriceSmart; no fee: Walmart, Target, Kroger,
Albertsons, Dollar General). It then estimates the club gap with year fixed effects, standard errors
clustered by company and an exact permutation test over every way of labeling three of the eight
companies as clubs.

The filings used are listed in data/raw/sec_filings.csv. Each document is fetched from www.sec.gov; if SEC
refuses the request (it rate-limits shared addresses), the script falls back to the Internet Archive's copy
of the same SEC address and says so. src/costco_membership.py imports the download and XBRL helpers here.

Usage (from the repository root):
    python src/warehouse_tariffs.py
Writes results/retail_tariffs.csv, results/retail_tariffs_by_year.csv and results/club_gap.csv.
"""

import html
import re
from itertools import combinations
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import pandas as pd
import requests
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "results"

HEADERS = {"User-Agent": "Brendyn Beasley research 83249437+brendynbeasley@users.noreply.github.com",
           "Accept-Encoding": "gzip, deflate"}
PAUSE = 0.35                     # seconds between SEC requests (SEC allows 10 a second; others share the IP)

CLUBS = {"Costco", "BJ's Wholesale", "PriceSmart"}  # every US-listed warehouse club with its own filings
WINDOW = range(2021, 2026)       # fiscal years in the cross-section (five complete recent years for all eight)

# XBRL elements tried in order for each line item. Total revenue includes membership fees where a
# company reports them, so merchandise sales = total revenue - fees. Operating costs are measured as
# revenue - cost of goods - operating income, which treats every company's expense lines alike.
TAGS = {
    "revenue": ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet"],
    "cogs": ["CostOfGoodsAndServicesSold", "CostOfRevenue", "CostOfGoodsSold", "MerchandiseCosts",
             "CostOfGoodsAndServiceExcludingDepreciationDepletionAndAmortization"],
    "opinc": ["OperatingIncomeLoss"],
    "fees": ["MembershipFees", "MembershipFeeIncome", "MembershipIncome", "RevenueFromMembershipFees",
             "RevenueFromEnrollmentAndRegistrationFeesExcludingHospitalityEnterprises"],
}


# ---------------------------------------------------------------- downloads


def fetch(url, path, sec=True, required=True):
    """Fetch url to path unless already cached; fall back to the Internet Archive copy if SEC refuses.
    With required=False a failed download returns None instead of stopping the script."""
    path = Path(path)
    if path.exists() and path.stat().st_size > 0:
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    time.sleep(PAUSE if sec else 0)
    r = requests.get(url, headers=HEADERS, timeout=300)
    source = "sec.gov" if sec else url.split("/")[2]
    if r.status_code != 200 and sec:
        r = archived_copy(url)
        source = "web.archive.org copy of the sec.gov address"
    if r.status_code != 200:
        if not required:
            print(f"  not available from sec.gov or the Internet Archive: {url}")
            return None
        raise SystemExit(f"Download failed ({r.status_code}) for {url}")
    tmp = path.with_suffix(path.suffix + ".part")
    tmp.write_bytes(r.content)
    tmp.rename(path)
    print(f"  fetched {url.split('/')[-1]} from {source} ({len(r.content) / 1e6:.1f} MB)")
    return path


def archived_copy(url):
    """The Internet Archive's most recent good (status 200) capture of a sec.gov address, as originally served."""
    r = None
    for attempt in range(5):
        time.sleep(2.0 * attempt)
        try:
            meta = requests.get("https://archive.org/wayback/available", params={"url": url}, timeout=60).json()
            snap = meta.get("archived_snapshots", {}).get("closest")
            if not snap or snap.get("status") != "200":
                return requests.Response() if r is None else r
            raw_url = re.sub(r"/web/(\d+)/", r"/web/\1id_/", snap["url"]).replace("http://", "https://", 1)
            r = requests.get(raw_url, headers=HEADERS, timeout=300)
        except (requests.RequestException, ValueError):
            continue
        if r.status_code == 200:
            return r
    return r if r is not None else requests.Response()


def fred_series(series_id):
    path = fetch(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}",
                 RAW / "fred" / f"{series_id}.csv", sec=False)
    df = pd.read_csv(path)
    df.columns = ["date", "value"]
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df.dropna()


def filing_documents(cik, accession):
    """Primary 10-K document and XBRL instance file named in a filing's EDGAR index page."""
    acc = accession.replace("-", "")
    base = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc}/"
    path = fetch(base + f"{accession}-index.htm", RAW / "sec" / f"{cik}_{acc}_index.htm", required=False)
    if path is None:
        return base, None, None
    page = path.read_text(errors="ignore")
    rows = re.findall(r'<a href="[^"]*/([^"/]+)"[^>]*>[^<]*</a>(?:(?!</td>).)*</td>\s*<td[^>]*>([^<]*)</td>', page, re.S)
    rows = [(f.split("?")[0], t.strip()) for f, t in rows]
    primary = next((f for f, t in rows if t in ("10-K", "10-K405") and f.endswith((".htm", ".html", ".txt"))
                    and "index" not in f), None)
    instance = next((f for f, t in rows if t == "EX-101.INS"), None)
    if instance is None:
        instance = next((f for f, _ in rows if f.endswith("_htm.xml")), None)
    return base, primary, instance


def filing_text(cik, accession):
    base, primary, _ = filing_documents(cik, accession)
    path = None if primary is None else fetch(base + primary, RAW / "sec" / f"{cik}_{accession.replace('-', '')}_{primary}",
                                              required=False)
    if path is None:
        print(f"  no 10-K text available for {accession}")
        return ""
    raw = path.read_text(errors="ignore")
    raw = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", raw)
    raw = re.sub(r"(?s)<[^>]+>", " ", raw)
    text = html.unescape(raw).replace("\xa0", " ").replace("’", "'")
    return re.sub(r"\s+", " ", text)


# ---------------------------------------------------------------- XBRL instance


def instance_facts(cik, accession):
    """Full-year facts in a filing's XBRL instance with no dimension or a single one (member is "" when none)."""
    base, _, instance = filing_documents(cik, accession)
    cols = ["element", "member", "start", "end", "value"]
    if instance is None:
        return pd.DataFrame(columns=cols)
    path = fetch(base + instance, RAW / "sec" / f"{cik}_{accession.replace('-', '')}_{instance}", required=False)
    if path is None:
        return pd.DataFrame(columns=cols)
    root = ET.parse(path).getroot()
    x = "{http://www.xbrl.org/2003/instance}"
    periods = {}
    for ctx in root.iter(x + "context"):
        seg = ctx.find(f"{x}entity/{x}segment")
        members = [m.text.strip() for m in seg] if seg is not None else []
        start, end = ctx.find(f"{x}period/{x}startDate"), ctx.find(f"{x}period/{x}endDate")
        if len(members) <= 1 and ctx.find(f"{x}scenario") is None and start is not None and end is not None:
            periods[ctx.get("id")] = (members[0] if members else "", start.text.strip(), end.text.strip())
    rows = []
    for el in root:
        ref = el.get("contextRef")
        if ref not in periods or not (el.text or "").strip():
            continue
        try:
            value = float(el.text.strip())
        except ValueError:
            continue
        rows.append((el.tag.split("}")[-1], *periods[ref], value))
    df = pd.DataFrame(rows, columns=cols)
    days = (pd.to_datetime(df.end) - pd.to_datetime(df.start)).dt.days
    return df[days.between(350, 380)].drop_duplicates(["element", "member", "start", "end"])


def fiscal_label(end):
    """Years ending in January or February are labeled by the prior calendar year (Walmart's year ending
    January 31, 2026 is fiscal 2025), which is how the retailers describe the bulk of the year."""
    end = pd.Timestamp(end)
    return end.year - 1 if end.month <= 2 else end.year


def annual_items(facts):
    """One row per fiscal year: revenue, cost of goods, operating income and membership fees.

    Totals come from facts without a dimension (earlier elements in each TAGS list win). Membership fees
    are reported as revenue broken out by a product member whose name contains "Membership". If a
    company reports cost of goods only by product line (PriceSmart), the lines are added up.
    """
    facts = facts.assign(fiscal_year=facts.end.map(fiscal_label))
    plain = facts[facts.member == ""]
    out = {}
    for item, tags in TAGS.items():
        for tag in tags:
            hit = plain[plain.element == tag]
            if len(hit):
                s = hit.groupby("fiscal_year").value.first()
                out[item] = out[item].combine_first(s) if item in out else s
    fee_rows = facts[facts.element.isin(TAGS["revenue"]) & facts.member.str.contains("Membership")
                     & ~facts.member.str.contains("Liabilit|Deferred")]
    if len(fee_rows):
        s = fee_rows.groupby("fiscal_year").value.first()
        out["fees"] = out["fees"].combine_first(s) if "fees" in out else s
    if "cogs" not in out:
        lines = facts[facts.element.isin(TAGS["cogs"]) & (facts.member != "")]
        if len(lines):
            out["cogs"] = lines.groupby(["fiscal_year", "member"]).value.first().groupby("fiscal_year").sum()
    return pd.DataFrame(out, columns=list(TAGS))


def income_statements(filings):
    """Line items by fiscal year from a set of filings; a later filing overrides an earlier one."""
    years = {}
    for _, f in filings.sort_values("fiscal_year").iterrows():
        for fy, row in annual_items(instance_facts(f.cik, f.accession)).iterrows():
            years[fy] = row.combine_first(years[fy]) if fy in years else row
    return pd.DataFrame(years).T.sort_index().astype(float)


def tariff_measures(df):
    d = df.copy()
    d["markup_over_cost_pct"] = 100 * (d.merch_sales - d.cogs) / d.cogs
    d["gross_margin_pct"] = 100 * (d.merch_sales - d.cogs) / d.merch_sales
    d["opex_pct"] = 100 * (d.revenue - d.cogs - d.opinc) / d.merch_sales   # everything between gross margin and operating income
    d["merch_margin_pct"] = 100 * (d.opinc - d.fees) / d.merch_sales
    d["fees_pct_sales"] = 100 * d.fees / d.merch_sales
    d["fees_share_of_opinc_pct"] = 100 * d.fees / d.opinc
    return d


# ---------------------------------------------------------------- outputs


def load_filings():
    filings = pd.read_csv(RAW / "sec_filings.csv")
    print(f"Loaded data/raw/sec_filings.csv: {len(filings)} 10-K filings from {filings.company.nunique()} companies")
    return filings


def retail_panel(filings):
    frames = []
    for company, group in filings.groupby("company", sort=False):
        if company == "Costco":
            group = group[group.fiscal_year.between(2021, 2026)]   # the same span of reports as everyone else
        df = income_statements(group)
        df.index.name = "fiscal_year"
        df = df.reset_index()
        df["company"], df["club"] = company, company in CLUBS
        if company not in CLUBS:
            df["fees"] = 0.0
        df["merch_sales"] = df.revenue - df.fees
        frames.append(df)
    return tariff_measures(pd.concat(frames, ignore_index=True))


def cross_section(panel):
    """Five-year totals per company, then the ratios (a ratio of sums, so larger years count more)."""
    need = ["revenue", "merch_sales", "cogs", "opinc", "fees"]
    w = panel[panel.fiscal_year.isin(WINDOW)]
    complete = w.dropna(subset=need)
    for _, r in w[~w.index.isin(complete.index)].iterrows():
        print(f"  dropped {r.company} fiscal {r.fiscal_year}: missing "
              f"{', '.join(c for c in need if pd.isna(r[c]))}")
    g = complete.groupby(["company", "club"])[need].sum()
    g["years"] = complete.groupby(["company", "club"]).size()
    g = tariff_measures(g.reset_index())
    return g.sort_values(["club", "merch_sales"], ascending=[False, False])


def club_gap(panel):
    """y_it = a + b Club_i + year effects + e_it on company-years in the window.

    Standard errors are clustered by company (eight clusters, so they are only a rough guide); the exact
    permutation p-value compares the estimated b with its value under all 56 ways of calling three of the
    eight companies clubs.
    """
    d = panel[panel.fiscal_year.isin(WINDOW)].dropna(subset=["markup_over_cost_pct", "merch_margin_pct"]).copy()
    companies = sorted(d.company.unique())
    rows = []
    for y in ["markup_over_cost_pct", "opex_pct", "merch_margin_pct"]:
        def fit(clubs):
            d["club_dummy"] = d.company.isin(clubs).astype(float)
            return smf.ols(f"{y} ~ club_dummy + C(fiscal_year)", data=d).fit(
                cov_type="cluster", cov_kwds={"groups": pd.factorize(d.company)[0]})
        res = fit(CLUBS)
        draws = [fit(set(c)).params["club_dummy"] for c in combinations(companies, len(CLUBS))]
        b = res.params["club_dummy"]
        p_perm = np.mean([abs(x) >= abs(b) - 1e-9 for x in draws])
        lo, hi = res.conf_int().loc["club_dummy"]
        rows.append(dict(outcome=y, beta_club=b, se_cluster=res.bse["club_dummy"], ci95_low=lo, ci95_high=hi,
                         p_cluster=res.pvalues["club_dummy"], p_permutation=p_perm, assignments=len(draws),
                         n=int(res.nobs), companies=len(companies)))
    out = pd.DataFrame(rows)
    out.to_csv(OUT / "club_gap.csv", index=False, float_format="%.4f")
    print("\nClub gap, company-years with year fixed effects:\n" + out.round(3).to_string(index=False))
    return out


def main():
    OUT.mkdir(exist_ok=True)
    filings = load_filings()

    panel = retail_panel(filings)
    panel.to_csv(OUT / "retail_tariffs_by_year.csv", index=False, float_format="%.4f")
    print(f"Income statements: {len(panel)} company-years, fiscal {panel.fiscal_year.min()}-{panel.fiscal_year.max()}")
    cs = cross_section(panel)
    cs.to_csv(OUT / "retail_tariffs.csv", index=False, float_format="%.3f")
    print("\nTariffs, fiscal 2021-2025 totals:")
    print(cs[["company", "years", "merch_sales", "markup_over_cost_pct", "opex_pct", "merch_margin_pct",
              "fees_pct_sales", "fees_share_of_opinc_pct"]].round(2).to_string(index=False))
    club_gap(panel)
    print("\nWrote retail_tariffs.csv, retail_tariffs_by_year.csv and club_gap.csv")


if __name__ == "__main__":
    main()
