"""Worked examples of Armstrong's (1996) exclusion result and Rochet-Chone (1998) bunching.

This is the small, secondary piece of the repository. It computes, on a fine grid of buyer types,
what a seller with zero marginal cost earns from simple menus for two goods, and what share of
buyers each menu turns away. Two textbook cases are used:

  * values for each good independent and uniform on [1, 2]: every buyer values every good above
    cost, a one-good seller serves everyone, and yet the best two-good menu excludes some buyers;
  * values independent and uniform on [0, 1]: the Manelli-Vincent (2006) optimal menu, sell
    either good for 2/3 or both for (4 - sqrt 2)/3, as restated by Daskalakis, Deckelbaum and
    Tzamos (2017, Example 1).

It also prints the arithmetic behind Armstrong's argument: raise every price by a small amount e,
gain about e from every buyer, and lose only the buyers in the bottom corner, whose number shrinks
like e squared when there are two goods but like e when there is one.

Usage (from the repository root):
    python src/screening_examples.py
Writes results/menu_examples.csv, results/epsilon_argument.csv, results/menu_grid_search.csv,
results/many_goods.csv and results/exclusion_corner.png.
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "results"

GRID = 1500                     # grid points per axis; midpoints of a GRID x GRID mesh of types
EPSILONS = [0.05, 0.10, 0.20]   # price increases used to show the first-order / second-order argument
SEARCH_STEP = 0.01              # step for the grid search over (single-good price, bundle price)
MANY_GOODS = [1, 2, 3, 5, 10, 20, 50, 100]   # numbers of goods for the bundle-only calculation
DRAWS = 200_000                 # simulated buyers per number of goods
SEED = 1996                     # fixed so the simulated table is reproducible


def type_grid(lo, hi, n=GRID):
    """Midpoints of an n x n mesh on [lo, hi]^2; every point carries equal probability."""
    pts = lo + (np.arange(n) + 0.5) * (hi - lo) / n
    v1, v2 = np.meshgrid(pts, pts, indexing="ij")
    return v1.ravel(), v2.ravel()


def run_menu(v1, v2, p1, p2, pb):
    """Each type picks the option with the highest surplus (ties go to buying more).

    Options are nothing, good 1 at p1, good 2 at p2, both at pb. Use np.inf to remove an option.
    Returns revenue per buyer type and the share of types that buy nothing.
    """
    surplus = np.column_stack([np.zeros_like(v1), v1 - p1, v2 - p2, v1 + v2 - pb])
    prices = np.array([0.0, p1, p2, pb])
    # prefer larger bundles on ties by scanning options from largest to smallest
    order = [3, 1, 2, 0]
    best = np.full(v1.shape, 0)
    best_s = np.full(v1.shape, -np.inf)
    for k in order:
        better = surplus[:, k] > best_s + 1e-12
        best = np.where(better, k, best)
        best_s = np.where(better, surplus[:, k], best_s)
    pay = prices[best]
    pay = np.where(np.isfinite(pay), pay, 0.0)
    return pay.mean(), (best == 0).mean(), best


def bundle_optimum_uniform12():
    """Closed form for the best pure-bundle price when both values are uniform on [1, 2].

    For p in [2, 3], P(v1 + v2 >= p) = 1 - (p - 2)^2 / 2, so revenue p (1 - x^2/2) with x = p - 2 has
    first-order condition 1 - 2x - 1.5 x^2 = 0, i.e. x = (sqrt(10) - 2) / 3.
    """
    x = (np.sqrt(10) - 2) / 3
    p = 2 + x
    return p, x * x / 2, p * (1 - x * x / 2)


def menu_table():
    rows = []
    a1, a2 = type_grid(1.0, 2.0)
    b1, b2 = type_grid(0.0, 1.0)
    inf = np.inf

    # One good, value uniform on [1, 2]: revenue p * P(v >= p) is maximized at p = 1.
    one = np.linspace(1.0, 2.0, 10001)
    rev_one = one * (2.0 - one)
    rows.append(dict(case="one good, value U[1,2]", menu="single price", p_single=one[rev_one.argmax()],
                     p_bundle=np.nan, revenue=rev_one.max(), share_excluded=0.0, share_one_good=1.0,
                     method="closed form"))

    # separate selling: buying both costs the sum of the two prices
    r, ex, ch = run_menu(a1, a2, 1.0, 1.0, 2.0)
    rows.append(dict(case="two goods, values U[1,2]", menu="separate prices", p_single=1.0, p_bundle=np.nan,
                     revenue=r, share_excluded=ex, share_one_good=np.isin(ch, [1, 2]).mean(), method="grid"))
    pb, ex_cf, rev_cf = bundle_optimum_uniform12()
    r, ex, _ = run_menu(a1, a2, inf, inf, pb)
    rows.append(dict(case="two goods, values U[1,2]", menu="bundle only", p_single=np.nan, p_bundle=pb,
                     revenue=r, share_excluded=ex, share_one_good=0.0, method="grid (closed form %.4f, %.4f)" % (rev_cf, ex_cf)))

    # grid search over symmetric mixed bundling menus for U[1,2]^2
    search = []
    for ps in np.arange(1.0, 2.0 + 1e-9, SEARCH_STEP * 5):
        for pbb in np.arange(2.0, 3.0 + 1e-9, SEARCH_STEP):
            if pbb > 2 * ps:          # a bundle dearer than two singles is never bought
                continue
            r, ex, _ = run_menu(a1[::7], a2[::7], ps, ps, pbb)
            search.append(dict(p_single=round(ps, 3), p_bundle=round(pbb, 3), revenue=r, share_excluded=ex))
    search = pd.DataFrame(search)
    best = search.loc[search.revenue.idxmax()]
    r, ex, ch = run_menu(a1, a2, best.p_single, best.p_single, best.p_bundle)
    rows.append(dict(case="two goods, values U[1,2]", menu="best menu found when single-good prices are also allowed",
                     p_single=best.p_single, p_bundle=best.p_bundle, revenue=r, share_excluded=ex,
                     share_one_good=np.isin(ch, [1, 2]).mean(), method="grid search"))

    r, ex, ch = run_menu(b1, b2, 0.5, 0.5, 1.0)
    rows.append(dict(case="two goods, values U[0,1]", menu="separate prices", p_single=0.5, p_bundle=np.nan,
                     revenue=r, share_excluded=ex, share_one_good=np.isin(ch, [1, 2]).mean(), method="grid"))
    pbu = np.sqrt(2 / 3)
    r, ex, _ = run_menu(b1, b2, inf, inf, pbu)
    rows.append(dict(case="two goods, values U[0,1]", menu="bundle only", p_single=np.nan, p_bundle=pbu,
                     revenue=r, share_excluded=ex, share_one_good=0.0, method="grid"))
    pmv = (4 - np.sqrt(2)) / 3
    r, ex, ch = run_menu(b1, b2, 2 / 3, 2 / 3, pmv)
    rows.append(dict(case="two goods, values U[0,1]", menu="Manelli-Vincent optimal menu", p_single=2 / 3,
                     p_bundle=pmv, revenue=r, share_excluded=ex, share_one_good=np.isin(ch, [1, 2]).mean(),
                     method="grid"))
    return pd.DataFrame(rows), search


def epsilon_table():
    """Gain and loss from raising the price by e above the no-exclusion price."""
    a1, a2 = type_grid(1.0, 2.0)
    rows = []
    for e in EPSILONS:
        # one good: price 1 -> 1 + e loses the buyers with v in [1, 1 + e], a share e
        lost1 = e
        rows.append(dict(goods=1, start_price=1.0, increase=e, gain_from_stayers=e * (1 - lost1),
                         revenue_lost_from_leavers=1.0 * lost1, share_lost=lost1,
                         revenue_before=1.0, revenue_after=(1 + e) * (1 - lost1)))
        # two goods sold as a bundle: price 2 -> 2 + e loses the corner v1 + v2 < 2 + e, a share e^2 / 2
        r, ex, _ = run_menu(a1, a2, np.inf, np.inf, 2.0 + e)
        rows.append(dict(goods=2, start_price=2.0, increase=e, gain_from_stayers=e * (1 - ex),
                         revenue_lost_from_leavers=2.0 * ex, share_lost=ex,
                         revenue_before=2.0, revenue_after=r))
    return pd.DataFrame(rows)


def many_goods_table():
    """Best single price for a bundle of n goods, values independent and uniform on [1, 2], zero cost.

    Each simulated buyer's value for the bundle is the sum of her n values. Sorting those sums, a price equal
    to the i-th smallest sum sells to the N - i buyers at or above it, so the revenue-maximizing price can be
    read off directly. With one good the seller serves everyone; Armstrong's exclusion appears at two goods
    and then shrinks as n grows, because independent tastes average out across many products.
    """
    rng = np.random.default_rng(SEED)
    rows = []
    for n in MANY_GOODS:
        sums = np.sort(rng.uniform(1.0, 2.0, (DRAWS, n)).sum(axis=1))
        revenue = sums * (DRAWS - np.arange(DRAWS)) / DRAWS
        i = int(revenue.argmax())
        rows.append(dict(goods=n, bundle_price_per_good=sums[i] / n, share_excluded=i / DRAWS,
                         revenue_per_good=revenue[i] / n, revenue_per_good_separate_selling=1.0))
    return pd.DataFrame(rows)


def corner_figure(bundle_price):
    """Type square for values uniform on [1, 2], coloured by whether the type buys the bundle."""
    n = 400
    a1, a2 = type_grid(1.0, 2.0, n)
    _, _, choice = run_menu(a1, a2, np.inf, np.inf, bundle_price)
    img = (choice.reshape(n, n).T == 3).astype(int)
    fig, ax = plt.subplots(figsize=(5.2, 4.6))
    colors = matplotlib.colors.ListedColormap(["#bdbdbd", "#3182bd"])
    ax.imshow(img, origin="lower", extent=[1, 2, 1, 2], cmap=colors, vmin=0, vmax=1, interpolation="nearest")
    xs = np.linspace(1, bundle_price - 1, 50)
    ax.plot(xs, bundle_price - xs, color="black", lw=1)
    ax.set_xlabel("Value of good 1 ($)")
    ax.set_ylabel("Value of good 2 ($)")
    ax.set_title("Both goods sold together for \\$%.2f\n(values uniform on \\$1 to \\$2, zero cost)" % bundle_price,
                 fontsize=10)
    ax.text(1.02, 1.04, "buys\nnothing", fontsize=8)
    ax.text(1.55, 1.6, "buys both", fontsize=10, color="white")
    fig.tight_layout()
    fig.savefig(OUT / "exclusion_corner.png", dpi=160)
    plt.close(fig)


def main():
    OUT.mkdir(exist_ok=True)
    print(f"Type grid: {GRID} x {GRID} = {GRID * GRID:,} equally likely buyer types per case")
    menus, search = menu_table()
    menus.to_csv(OUT / "menu_examples.csv", index=False, float_format="%.4f")
    search.to_csv(OUT / "menu_grid_search.csv", index=False, float_format="%.5f")
    print(menus.to_string(index=False))
    eps = epsilon_table()
    eps.to_csv(OUT / "epsilon_argument.csv", index=False, float_format="%.5f")
    print(eps.to_string(index=False))
    many = many_goods_table()
    many.to_csv(OUT / "many_goods.csv", index=False, float_format="%.4f")
    print(many.round(4).to_string(index=False))
    corner_figure(bundle_optimum_uniform12()[0])
    print("Wrote menu_examples.csv, menu_grid_search.csv, epsilon_argument.csv, many_goods.csv, exclusion_corner.png")


if __name__ == "__main__":
    main()
