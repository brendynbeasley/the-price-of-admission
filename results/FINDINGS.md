# Armstrong (1996) on modern data: findings

## In plain English

Mark Armstrong showed in 1996 that a seller of many products, facing buyers whose tastes differ in several ways,
does best with a price list that leaves some buyers out entirely, and that in the cases he could solve the best
price list charges for a basket according to what it cost. Warehouse clubs come closest to that design. This study
measures how close.

- **The clubs sell close to cost and earn at the door.** Costco, BJ's Wholesale and PriceSmart mark goods up 12% to
  20% over cost, against 29% to 44% at Walmart, Target, Kroger, Albertsons and Dollar General, and membership fees
  supply 35% to 57% of their operating income.
- **Costco has drifted from the pure design.** Fees were 86% of Costco's operating income in fiscal 2009 and 51% in
  fiscal 2026, as the margin on merchandise rose from 0.35% to 1.94% of sales.
- **A two-line menu sorts members by appetite.** Costco's 42.3 million Executive members ($130 a year, 2% reward)
  spend $5,284 each and make 75.2% of sales; the other 41.8 million spend $1,764. At least 39.9% of US households held
  no Costco membership in fiscal 2025.
- **Fee increases cost almost nothing in members.** The last three $5 increases left the US and Canada renewal rate unchanged within noise
  ($`\hat\delta = -0.32`$, permutation p = 0.44); the worst-case loss from the 2024 increase, $56 million, was under a
  third of the $198 million Costco reported gaining.

A friendlier tour is in the [README](../README.md); method and test statistics are in [TECHNICAL.md](../TECHNICAL.md).

## Key to the labels

- *markup_over_cost_pct*: (merchandise sales − cost of goods) ÷ cost of goods, percent.
- *gross_margin_pct*: (merchandise sales − cost of goods) ÷ merchandise sales.
- *opex_pct*: operating costs, measured as revenue − cost of goods − operating income, ÷ merchandise sales.
- *merch_margin_pct*: (operating income − membership fees) ÷ merchandise sales, the margin left on goods.
- *fees_pct_sales*, *fees_share_of_opinc_pct*: membership fees ÷ merchandise sales, and ÷ operating income.
- *club*: True for Costco, BJ's Wholesale and PriceSmart. Fiscal years ending in January or February are labeled by
  the previous calendar year. Dollar amounts marked *_bn* are billions; *_k* are thousands.
- *renewal_unsplit*: the single renewal rate Costco reported before it split out the US and Canada in fiscal 2010
  (the column repeats the US and Canada rate for 2010 to 2015, where the parser also matched it).
- *max_loss_musd*, *reported_gain_first_full_year_musd*: millions of dollars.

## Tables

### retail_tariffs.csv

| company | club | years | merch_sales_bn | fees_bn | opinc_bn | markup_over_cost_pct | gross_margin_pct | opex_pct | merch_margin_pct | fees_pct_sales | fees_share_of_opinc_pct |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Costco | True | 5 | 1172.0 | 22.8 | 42.3 | 12.17 | 10.85 | 9.19 | 1.66 | 1.95 | 54.00 |
| BJ's Wholesale | True | 5 | 95.8 | 2.1 | 3.7 | 19.73 | 16.48 | 14.80 | 1.68 | 2.23 | 57.01 |
| PriceSmart | True | 4 | 16.8 | 0.3 | 0.7 | 18.99 | 15.96 | 13.14 | 2.82 | 1.54 | 35.34 |
| Walmart | False | 5 | 3226.3 | 0.0 | 132.6 | 32.77 | 24.68 | 20.57 | 4.11 | 0.00 | 0.00 |
| Kroger | False | 5 | 731.0 | 0.0 | 16.4 | 28.77 | 22.34 | 20.09 | 2.25 | 0.00 | 0.00 |
| Target | False | 5 | 533.9 | 0.0 | 29.2 | 37.91 | 27.49 | 22.02 | 5.47 | 0.00 | 0.00 |
| Albertsons | False | 5 | 392.3 | 0.0 | 9.1 | 38.66 | 27.88 | 25.57 | 2.32 | 0.00 | 0.00 |
| Dollar General | False | 5 | 194.1 | 0.0 | 12.9 | 44.17 | 30.64 | 23.99 | 6.65 | 0.00 | 0.00 |

### club_gap.csv

| outcome | beta_club | se_cluster | ci95_low | ci95_high | p_cluster | p_permutation | assignments | n | companies |
|---|---|---|---|---|---|---|---|---|---|
| markup_over_cost_pct | -19.678 | 3.627 | -26.786 | -12.571 | 0.000 | 0.018 | 56 | 39 | 8 |
| opex_pct | -10.043 | 1.985 | -13.933 | -6.153 | 0.000 | 0.018 | 56 | 39 | 8 |
| merch_margin_pct | -2.255 | 0.943 | -4.104 | -0.406 | 0.017 | 0.125 | 56 | 39 | 8 |

### costco_history.csv (selected columns)

| fiscal_year | fee_us_gold_star | fee_in_2025_dollars | paid_members_k | cardholders_k | exec_members_k | exec_share_of_sales_pct | renewal_us_canada | renewal_worldwide | renewal_unsplit | merch_sales_bn | fees_bn | opinc_bn | markup_over_cost_pct | merch_margin_pct | fees_pct_sales | fees_share_of_opinc_pct |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2005 | 45 | 74.20 |  |  |  |  |  |  | 86 |  |  |  |  |  |  |  |
| 2006 | 50 | 79.87 | 22,552 | 47,679 | 5,187 | 45 |  |  | 86.5 |  |  |  |  |  |  |  |
| 2007 | 50 | 77.64 | 24,000 | 50,400 |  |  |  |  | 87 |  |  |  |  |  |  |  |
| 2008 | 50 | 74.79 | 25,800 | 53,500 | 6,708 |  |  |  | 87 | 71.0 | 1.51 | 1.97 | 11.77 | 0.65 | 2.12 | 76.5 |
| 2009 | 50 | 75.03 | 30,600 | 56,000 | 8,874 |  |  |  | 87 | 69.9 | 1.53 | 1.78 | 12.12 | 0.35 | 2.19 | 86.3 |
| 2010 | 50 | 73.82 | 31,600 | 58,000 | 11,376 |  | 88 |  | 88 | 76.3 | 1.69 | 2.08 | 12.15 | 0.51 | 2.22 | 81.4 |
| 2011 | 50 | 71.57 | 35,300 | 64,000 | 13,414 |  | 89 | 86 | 89 | 87.0 | 1.87 | 2.44 | 11.97 | 0.66 | 2.14 | 76.5 |
| 2012 | 55 | 77.13 | 36,900 | 67,000 | 14,022 |  | 89.7 | 86.4 | 89.7 | 97.1 | 2.08 | 2.76 | 11.79 | 0.70 | 2.14 | 75.2 |
| 2013 | 55 | 76.02 | 39,000 | 71,200 |  |  | 90 | 86 | 90 | 102.9 | 2.29 | 3.05 | 11.88 | 0.75 | 2.22 | 74.9 |
| 2014 | 55 | 74.81 | 42,000 | 76,400 |  |  | 91 | 87 | 91 | 110.2 | 2.43 | 3.22 | 11.94 | 0.72 | 2.20 | 75.4 |
| 2015 | 55 | 74.72 | 44,600 | 81,300 |  |  | 91 | 88 | 91 | 113.7 | 2.53 | 3.62 | 12.47 | 0.96 | 2.23 | 69.9 |
| 2016 | 55 | 73.78 | 47,600 | 86,700 |  |  | 90 | 88 |  | 116.1 | 2.65 | 3.67 | 12.80 | 0.88 | 2.28 | 72.1 |
| 2017 | 60 | 78.81 | 49,400 | 90,300 | 18,772 |  | 90 | 87 |  | 126.2 | 2.85 | 4.11 | 12.77 | 1.00 | 2.26 | 69.4 |
| 2018 | 60 | 76.93 | 51,600 | 94,300 |  |  | 90 | 88 |  | 138.4 | 3.14 | 4.48 | 12.41 | 0.97 | 2.27 | 70.1 |
| 2019 | 60 | 75.56 | 53,900 | 98,500 |  |  | 91 | 88 |  | 149.4 | 3.35 | 4.74 | 12.39 | 0.93 | 2.24 | 70.8 |
| 2020 | 60 | 74.63 | 58,100 | 105,500 |  |  | 91 | 88 |  | 163.2 | 3.54 | 5.43 | 12.61 | 1.16 | 2.17 | 65.2 |
| 2021 | 60 | 71.29 | 61,700 | 111,600 |  |  | 91 | 89 |  | 192.1 | 3.88 | 6.71 | 12.52 | 1.47 | 2.02 | 57.8 |
| 2022 | 60 | 66.01 | 65,800 | 118,900 |  | 71 | 93 | 90 |  | 222.7 | 4.22 | 7.79 | 11.71 | 1.60 | 1.90 | 54.2 |
| 2023 | 60 | 63.40 | 71,000 | 127,900 | 32,300 | 72.8 | 92.7 | 90.4 |  | 237.7 | 4.58 | 8.11 | 11.82 | 1.49 | 1.93 | 56.4 |
| 2024 | 60 | 61.58 | 76,200 | 136,800 | 35,400 | 73.3 | 92.9 | 90.5 |  | 249.6 | 4.83 | 9.29 | 12.26 | 1.79 | 1.93 | 52.0 |
| 2025 | 65 | 65.00 | 81,000 | 145,200 | 38,700 | 73.6 | 92.3 | 89.8 |  | 269.9 | 5.32 | 10.38 | 12.52 | 1.87 | 1.97 | 51.3 |
| 2026 | 65 | 63.07 | 84,100 | 150,400 | 42,300 | 75.2 | 92.3 | 89.8 |  | 297.2 | 5.91 | 11.69 | 12.47 | 1.94 | 1.99 | 50.6 |

### costco_menu.csv

| fiscal_year | tier | members_k | share_of_sales_pct | sales_per_member | us_fee | executive_breakeven_spend |
|---|---|---|---|---|---|---|
| 2026 | Executive | 42,300 | 75.2 | 5,284.39 | 130 | 3250 |
| 2026 | Gold Star and Business | 41,800 | 24.8 | 1,763.57 | 65 | 3250 |

### costco_exclusion.csv

| fiscal_year | paid_members_worldwide_k | us_households_k | max_share_of_us_households_pct | min_share_without_card_pct |
|---|---|---|---|---|
| 2006 | 22,552 | 114,384 | 19.7 | 80.3 |
| 2007 | 24,000 | 116,011 | 20.7 | 79.3 |
| 2008 | 25,800 | 116,783 | 22.1 | 77.9 |
| 2009 | 30,600 | 117,181 | 26.1 | 73.9 |
| 2010 | 31,600 | 117,538 | 26.9 | 73.1 |
| 2011 | 35,300 | 119,927 | 29.4 | 70.6 |
| 2012 | 36,900 | 121,084 | 30.5 | 69.5 |
| 2013 | 39,000 | 122,459 | 31.9 | 68.2 |
| 2014 | 42,000 | 123,229 | 34.1 | 65.9 |
| 2015 | 44,600 | 124,587 | 35.8 | 64.2 |
| 2016 | 47,600 | 125,819 | 37.8 | 62.2 |
| 2017 | 49,400 | 126,224 | 39.1 | 60.9 |
| 2018 | 51,600 | 127,586 | 40.4 | 59.6 |
| 2019 | 53,900 | 128,579 | 41.9 | 58.1 |
| 2020 | 58,100 | 128,451 | 45.2 | 54.8 |
| 2021 | 61,700 | 129,224 | 47.8 | 52.2 |
| 2022 | 65,800 | 131,202 | 50.1 | 49.9 |
| 2023 | 71,000 | 131,434 | 54.0 | 46.0 |
| 2024 | 76,200 | 132,216 | 57.6 | 42.4 |
| 2025 | 81,000 | 134,790 | 60.1 | 39.9 |

### fee_increases.csv

| increase_fiscal_year | fee_before | fee_after | renewal_year_before | renewal_lowest_two_years_after | renewal_change | paid_members_year_before_k | merch_margin_per_member | max_members_lost_k | max_loss_musd | reported_gain_first_full_year_musd |
|---|---|---|---|---|---|---|---|---|---|---|
| 2006 | 45.00 | 50.00 | 86.00 | 86.50 | 0.50 |  |  |  |  |  |
| 2012 | 50.00 | 55.00 | 89.00 | 89.70 | 0.70 | 35300.00 | 16.20 | 0.00 | 0.00 | 119.00 |
| 2017 | 55.00 | 60.00 | 90.00 | 90.00 | 0.00 | 47600.00 | 21.55 | 0.00 | 0.00 | 178.00 |
| 2025 | 60.00 | 65.00 | 92.90 | 92.30 | -0.60 | 76200.00 | 58.49 | 457.20 | 56.46 | 198.00 |

### renewal_test.csv

| measure | mean_increase_years | mean_other_years | delta_hat | se_hc1 | ci95_low | ci95_high | p_hc1 | permutation_p | n_increase_years | n_other_years | n | years |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| change in US and Canada renewal rate (points) | 0.067 | 0.390 | -0.323 | 0.323 | -0.957 | 0.310 | 0.317 | 0.440 | 6 | 10 | 16 | 2011-2026 |

### menu_examples.csv

| case | menu | p_single | p_bundle | revenue | share_excluded | share_one_good | method |
|---|---|---|---|---|---|---|---|
| one good, value U[1,2] | single price | 1.0000 |  | 1.0000 | 0.0000 | 1.0000 | closed form |
| two goods, values U[1,2] | separate prices | 1.0000 |  | 2.0000 | 0.0000 | 0.0000 | grid |
| two goods, values U[1,2] | bundle only |  | 2.3874 | 2.2080 | 0.0751 | 0.0000 | grid (closed form 2.2083, 0.0750) |
| two goods, values U[1,2] | best menu found when single-good prices are also allowed | 1.4000 | 2.3900 | 2.2086 | 0.0759 | 0.0000 | grid search |
| two goods, values U[0,1] | separate prices | 0.5000 |  | 0.5000 | 0.2500 | 0.5000 | grid |
| two goods, values U[0,1] | bundle only |  | 0.8165 | 0.5444 | 0.3332 | 0.0000 | grid |
| two goods, values U[0,1] | Manelli-Vincent optimal menu | 0.6667 | 0.8619 | 0.5493 | 0.3332 | 0.1302 | grid |

### epsilon_argument.csv

| goods | start_price | increase | gain_from_stayers | revenue_lost_from_leavers | share_lost | revenue_before | revenue_after |
|---|---|---|---|---|---|---|---|
| 1 | 1.0000 | 0.0500 | 0.0475 | 0.0500 | 0.0500 | 1.0000 | 0.9975 |
| 2 | 2.0000 | 0.0500 | 0.0499 | 0.0025 | 0.0012 | 2.0000 | 2.0475 |
| 1 | 1.0000 | 0.1000 | 0.0900 | 0.1000 | 0.1000 | 1.0000 | 0.9900 |
| 2 | 2.0000 | 0.1000 | 0.0995 | 0.0099 | 0.0050 | 2.0000 | 2.0896 |
| 1 | 1.0000 | 0.2000 | 0.1600 | 0.2000 | 0.2000 | 1.0000 | 0.9600 |
| 2 | 2.0000 | 0.2000 | 0.1960 | 0.0399 | 0.0199 | 2.0000 | 2.1561 |

### many_goods.csv

| goods | bundle_price_per_good | share_excluded | revenue_per_good | revenue_per_good_separate_selling |
|---|---|---|---|---|
| 1 | 1.0033 | 0.0029 | 1.0003 | 1.0000 |
| 2 | 1.1953 | 0.0770 | 1.1032 | 1.0000 |
| 3 | 1.2402 | 0.0627 | 1.1625 | 1.0000 |
| 5 | 1.2765 | 0.0417 | 1.2232 | 1.0000 |
| 10 | 1.3283 | 0.0297 | 1.2888 | 1.0000 |
| 20 | 1.3643 | 0.0169 | 1.3413 | 1.0000 |
| 50 | 1.4089 | 0.0126 | 1.3911 | 1.0000 |
| 100 | 1.4282 | 0.0063 | 1.4193 | 1.0000 |

`menu_grid_search.csv` holds every symmetric menu tried in the grid search (not reproduced here).
