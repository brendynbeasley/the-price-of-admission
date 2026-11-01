# Technical notes

Technical companion to the [README](README.md). Every table is in [results/FINDINGS.md](results/FINDINGS.md).

## The original study

Mark Armstrong, "Multiproduct Nonlinear Pricing," *Econometrica* 64(1), 1996, pp. 51–75, read with Jean-Charles
Rochet and Philippe Choné, "Ironing, Sweeping, and Multidimensional Screening," *Econometrica* 66(4), 1998,
pp. 783–826. Armstrong shows that when buyers' private tastes have more than one dimension, a profit-maximizing
seller always excludes a positive measure of low-value buyers from every market, and that in a class of cases
solved by a multivariate integration by parts the optimal tariff is cost-based. Rochet and Choné show that bunching
is generic in multidimensional screening. These are qualitative results; the paper has no data and no single
headline number. I verified them against the abstract on the Econometric Society's site, Armstrong's survey
"Nonlinear Pricing" (MPRA paper 65779, 2015), which cites the exclusion result to section 3 of the 1996 paper, and
Daskalakis, Deckelbaum and Tzamos (2017, arXiv 1409.4150), whose Example 1 restates the Manelli–Vincent (2006)
optimal menu for two goods with values uniform on [0, 1]: either good at 2/3, both at (4 − √2)/3.

## Headline results

| Test | Estimate | Uncertainty | N |
|---|---|---|---|
| Club gap in markup over cost of goods (points) | −19.7 | SE 3.6 (clustered by company); exact permutation p = 0.018 | 39 company-years |
| Club gap in operating costs per $ of sales (points) | −10.0 | SE 2.0; permutation p = 0.018 | 39 |
| Club gap in margin left on merchandise (points) | −2.3 | SE 0.9; permutation p = 0.125 | 39 |
| Fees as share of operating income, fiscal 2021–25 | Costco 54%, BJ's 57%, PriceSmart 35% | ratio of five-year sums | 3 clubs |
| Costco fee share of operating income | 86% (fiscal 2009) to 51% (fiscal 2026) | annual | 19 years |
| Lower bound on US households without a Costco card, fiscal 2025 | 39.9% | bound, not an estimate | 1 |
| Effect of a fee increase on the US and Canada renewal rate (points) | −0.32 | SE 0.32 (HC1); permutation p = 0.44 | 16 yearly changes |
| 2024 fee increase, worst-case loss against reported gain | $56 million vs $198 million | upper bound | 1 event |

## Data

- `data/raw/sec_filings.csv` lists the 58 annual reports used, by company, fiscal year and accession number: Costco
  fiscal 2005 to 2026, and fiscal 2021 to 2025 (PriceSmart to 2026) for BJ's Wholesale, PriceSmart, Walmart, Target,
  Kroger, Albertsons and Dollar General. The scripts read each filing's index page, 10-K document and XBRL instance (`*_htm.xml` or the `EX-101.INS` file), caching them in `data/raw/sec/` (git-ignored, about
  150 MB). When sec.gov refused requests, the script used the Internet Archive's most recent status-200 capture of
  the same sec.gov address, unchanged. Three documents were available from neither source: BJ's fiscal 2024 instance
  (its years are covered by the fiscal 2025 report), PriceSmart's fiscal 2025 instance, and PriceSmart's fiscal
  2026 index page, so PriceSmart enters the cross-section for 2021 to 2024 only.
- `data/raw/fred/TTLHH.csv`, total US households (Census Bureau, via FRED), and `data/raw/fred/CPIAUCSL.csv`,
  consumer price index (BLS, via FRED). Downloaded 1 November 2026.

## Method

Rules fixed before looking at results:

- Fiscal years ending in January or February are labeled by the previous calendar year, so Walmart's year ending
  31 January 2026 is fiscal 2025.
- From each XBRL instance I keep full-year facts (350 to 380 days) with no dimension. Revenue is the first of
  `Revenues`, `RevenueFromContractWithCustomerExcludingAssessedTax`, `SalesRevenueNet`; cost of goods the first of
  `CostOfGoodsAndServicesSold`, `CostOfRevenue`, `CostOfGoodsSold`, `MerchandiseCosts` and the
  excluding-depreciation variant; operating income `OperatingIncomeLoss`. Membership fees are revenue reported under
  a single product member whose name contains "Membership" (the recent filings of all three clubs) or the older
  undimensioned elements (Costco used `RevenueFromEnrollmentAndRegistrationFeesExcludingHospitalityEnterprises`).
  PriceSmart reports cost of goods only by product line, which I sum. A later filing overrides an earlier one.
- Merchandise sales are revenue minus fees. Operating costs are revenue minus cost of goods minus operating income,
  the same for every company. With $`S`$ merchandise sales, $`C`$ cost of goods, $`F`$ fees
  and $`\Pi`$ operating income,

```math
\begin{aligned}
m &= \frac{S - C}{C}, \qquad o = \frac{S + F - C - \Pi}{S}, \\
\text{margin left} &= \frac{\Pi - F}{S} = \frac{S - C}{S} - o, \qquad \text{fee share} = \frac{F}{\Pi}.
\end{aligned}
```

- Cross-section ratios use five-year sums. The regression is

```math
y_{it} = \alpha + \beta\,\text{Club}_i + \lambda_t + e_{it}, \qquad H_0:\ \beta = 0,
```

  estimated by OLS on company-years 2021 to 2025, with standard errors clustered by company and an exact
  permutation p-value over all 56 assignments of the club label to three of the eight companies.
- Costco's membership facts are read from 10-K text with regular expressions written for the phrasings used from
  fiscal 2005 to 2026; matches are printed for checking. Renewal rates are the US and Canada rate from fiscal 2010
  and, before that, the single rate Costco reported without naming countries. The US Gold Star fee is $45 before fiscal 2006 plus $5 per increase, as the parsed fee statements confirm. Executive counts come from the share of paid members (to fiscal
  2017) or the stated count (from fiscal 2023, each report also giving the prior year).
- Exclusion bound: one minus worldwide paid memberships divided by US households.
- Fee increases take effect in fiscal 2006, 2012, 2017 and 2025. The worst-case loss counts only lost renewals, not deterred new members. It treats any fall in the renewal
  rate, from the year before to the lower of the two years after, as members lost, applied to all paid members of
  the year before, each costing the new fee plus the average merchandise margin per member:

```math
\begin{aligned}
L^{\max} &= \max\bigl(r_{t-1} - \min(r_t, r_{t+1}),\, 0\bigr) \times N_{t-1} \\
&\quad \times \left(f_t + \frac{\Pi_{t-1} - F_{t-1}}{N_{t-1}}\right).
\end{aligned}
```

  Here $`r_t`$ is the renewal rate, $`N_t`$ paid members, $`f_t`$ the new US fee per member, and $`F`$ and $`\Pi`$
  total fee revenue and operating income. The gain is Costco's reported first-full-year effect: $119 million (fiscal 2013 report), $178 million (fiscal
  2018 report), and 40% of fiscal 2025's growth in fee revenue. The renewal regression is

```math
\Delta r_t = \alpha + \delta\,\text{Inc}_t + u_t, \qquad H_0:\ \delta = 0,
```

  for the yearly changes from fiscal 2011 to 2026 (the 2012, 2017 and 2025 increases), where $`\text{Inc}_t`$ marks an increase year or the year after, with HC1 standard errors
  and a 100,000-draw permutation test (seed 2017).
- Worked examples (`src/screening_examples.py`): zero cost, 1,500 × 1,500 grid of equally likely types, each type
  choosing the option with the highest surplus. The many-goods table simulates 200,000 buyers per case (seed 1996);
  its one-good row shows 0.3% excluded from sampling noise, where the exact answer is zero.

## Full test statistics

| Outcome | $`\hat\beta`$ | Clustered SE | 95% CI | Cluster p | Permutation p |
|---|---|---|---|---|---|
| Markup over cost of goods | −19.68 | 3.63 | [−26.79, −12.57] | < 0.001 | 0.018 |
| Operating costs per $ of sales | −10.04 | 1.98 | [−13.93, −6.15] | < 0.001 | 0.018 |
| Margin left on merchandise | −2.25 | 0.94 | [−4.10, −0.41] | 0.017 | 0.125 |

The smallest possible permutation p-value with 56 assignments is 0.018. With eight clusters the clustered standard
errors understate uncertainty, which is why the permutation p-values carry the inference.

| Renewal test | Value |
|---|---|
| Mean change, increase years and the year after (6 years) | +0.07 points |
| Mean change, other years (10 years) | +0.39 points |
| $`\hat\delta`$ (HC1 SE) | −0.32 (0.32), 95% CI [−0.96, 0.31], p = 0.32 |
| Permutation p | 0.44 |

| Worked example | Revenue per buyer | Share excluded |
|---|---|---|
| One good, value uniform on [1, 2], price 1 | 1.000 | 0% |
| Two goods, uniform on [1, 2], separate prices of 1 | 2.000 | 0% |
| Two goods, uniform on [1, 2], bundle at 2.387 | 2.208 | 7.5% |
| Two goods, uniform on [0, 1], separate prices of 1/2 | 0.500 | 25.0% |
| Two goods, uniform on [0, 1], bundle at 0.816 | 0.544 | 33.3% |
| Two goods, uniform on [0, 1], Manelli–Vincent menu | 0.549 | 33.3% |

## Reproducing the results

```bash
pip install -r requirements.txt
python src/screening_examples.py
python src/warehouse_tariffs.py
python src/costco_membership.py
```

Run from the repository root, in order. The first run downloads about 150 MB.

## Repository layout

| Path | What it is |
|---|---|
| [src/screening_examples.py](src/screening_examples.py) | Worked examples of exclusion and bunching |
| [src/warehouse_tariffs.py](src/warehouse_tariffs.py) | Downloads, XBRL parsing, retailer cross-section, club regression |
| [src/costco_membership.py](src/costco_membership.py) | Costco 10-K history, menu, exclusion bound, fee-increase extension |
| [results/FINDINGS.md](results/FINDINGS.md) | Summary and every table |
| `data/raw/` | Filing list and FRED series |

## References

- Armstrong, M. (1996). Multiproduct nonlinear pricing. *Econometrica* 64(1), 51–75.
- Armstrong, M. (2015). Nonlinear pricing. Munich Personal RePEc Archive, Paper 65779.
- Armstrong, M. & Vickers, J. (2001). Competitive price discrimination. *RAND Journal of Economics* 32(4).
- Armstrong, M., Cowan, S. & Vickers, J. (1994). *Regulatory Reform: Economic Analysis and British Experience*.
  MIT Press.
- Daskalakis, C., Deckelbaum, A. & Tzamos, C. (2017). Strong duality for a multiple-good monopolist.
  *Econometrica* 85(3), 735–767.
- Manelli, A. & Vincent, D. (2006). Bundling as an optimal selling mechanism for a multiple-good monopolist.
  *Journal of Economic Theory* 127(1), 1–35.
- Rochet, J.-C. & Choné, P. (1998). Ironing, sweeping, and multidimensional screening. *Econometrica* 66(4),
  783–826.
