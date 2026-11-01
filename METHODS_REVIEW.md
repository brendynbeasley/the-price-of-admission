# Methods review: Armstrong (1996), with Rochet and Choné (1998)

- **Paper:** Mark Armstrong, "Multiproduct Nonlinear Pricing," *Econometrica* 64(1), January 1996, pp. 51–75
  (DOI 10.2307/2171924). Read alongside its companion on the reading list, Jean-Charles Rochet and Philippe Choné,
  "Ironing, Sweeping, and Multidimensional Screening," *Econometrica* 66(4), July 1998, pp. 783–826.
- **Statistical focus:** the exclusion result (a profit-maximizing seller facing buyers with several-dimensional
  private tastes always leaves a positive measure of low-value buyers unserved) and the claim that, in the class of
  cases the paper solves explicitly, the optimal tariff is cost-based. For Rochet and Choné, the claim that bunching
  is a generic feature of the solution.
- **Review standard:** internal consistency of the formal results, explicitness of the assumptions, and the
  testability of the predictions. Data-policy standards (the AEA Data and Code Availability Policy) apply only to the
  numerical examples, since neither paper uses data.
- **What was read:** the abstract of Armstrong (1996) on the Econometric Society's publication page; Mark Armstrong's
  own survey "Nonlinear Pricing" (Munich Personal RePEc Archive paper 65779, July 2015), which restates the 1996
  results and cites them by section (section 3 for exclusion, section 4.4 for the solvable example) and summarizes the
  numerical example in Rochet and Choné (1998, section 7.2); and Daskalakis, Deckelbaum and Tzamos, "Strong Duality
  for a Multiple-Good Monopolist" (arXiv 1409.4150, v3, 2017), which restates the exclusion result and the
  Manelli–Vincent optimal menu. I did not read the full text of either *Econometrica* article, which sit behind JSTOR
  and Wiley. Everything below about the papers' internal structure comes from those three sources, and anything
  that would need the full text is listed under items requiring expert verification.

---

## Methods summary

Armstrong (1996) is a theory paper in mechanism design. A single seller offers several products. Each buyer's
tastes are described by a vector of parameters, one or more per product, that only the buyer knows. The seller
chooses a tariff, a schedule giving the payment for every possible bundle of quantities, to maximize expected profit,
and each buyer either picks the bundle that suits her best or buys nothing. The paper's contribution is to relax the
standard assumption that all private information can be captured in a single number. Two results carry it. First,
under the assumptions summarized in the survey (gross utility convex and homogeneous of degree one in the taste
parameters), the seller always chooses to exclude some low-value buyers from every market. Second, using a
multivariate form of integration by parts, the paper finds a class of cases with explicit solutions, and in those
cases the optimal tariff is cost-based, meaning the payment for a bundle depends on the bundle only through its cost.

The intuition for exclusion, as Armstrong's survey and later work present it, is a comparison of orders of
magnitude. Raising every payment by a small amount e earns about e from each buyer who stays. Only buyers whose
surplus was below e leave. With one dimension of taste that group has measure proportional to e, so the trade-off
can go either way. With two or more dimensions the low-surplus buyers sit in a corner of the type space whose
measure shrinks faster than e, so the gain always wins near zero exclusion.

Rochet and Choné (1998) study a general multidimensional screening problem and show that the conditions that rule
out bunching in one-dimensional models (monotone hazard rates and similar) do not carry over. In their framework,
bunching, where buyers with different tastes receive the same bundle, is generic. Their worked example, as Armstrong's
survey describes it, has three regions: buyers with low total taste are excluded, buyers with intermediate total
taste are bunched on a common bundle of the two products, and buyers with high total taste each receive a distinct
bundle. That example is solved numerically.

## Design and reporting items

Both papers are formal theory. Most of the items below are written for empirical work, and I say for each whether it
applies. Where it does, the "statistics" are the formal results and the numerical example.

### Research design

A mechanism-design model: one seller, a known distribution of buyer tastes, a tariff chosen to maximize expected
profit subject to each buyer choosing her best bundle or nothing. The design is deductive. Results follow from stated
assumptions, not from observation.

### Sampling strategy

Does not apply. Neither paper draws a sample. Rochet and Choné's example (as the survey describes it) is computed on
an assumed distribution of types, which plays the role a population would play in empirical work.

### Sample size

Does not apply. No observations are used. The size of the grid used for Rochet and Choné's numerical solution is not
reported in the sources I read.

### Inclusion and exclusion criteria

Does not apply to data. The analogous items are the model's restrictions on preferences (in the survey's summary,
gross utility convex and homogeneous of degree one in the taste parameters) and on the type distribution. The exact
support conditions need the full text and are listed for expert verification.

### Independent and dependent variables

Does not apply in the regression sense. The primitives are the buyer's taste vector and the seller's cost; the
outcomes are the tariff, the allocation and the set of excluded types.

### Statistical methods

None. Armstrong's explicit solutions rest on a multivariate form of integration by parts (abstract), and Rochet and
Choné solve their worked example numerically (survey). The proof techniques beyond that need the full text.

### Reported effect sizes

The results are qualitative (a positive measure excluded, bunching generic, a cost-based tariff in a solvable class).
The sources I read quote no numerical magnitude from either paper.

### Confidence intervals

Do not apply. The results are exact statements within the model.

### P-values

Do not apply.

### Missing data treatment

Does not apply.

### Stated limitations

As the survey reports them, the explicit solutions cover only a special class (independent scale and relative-taste
parameters), and the general multidimensional problem was not solved analytically. Both papers assume a single
seller who commits to a tariff and knows the distribution of tastes.

## Statistics extraction table

| Statistic | Value and unit | Source location | What it measures | What it does not establish |
|---|---|---|---|---|
| Exclusion result | Qualitative: a positive measure of buyer types buys nothing at the optimum | Armstrong (1996), section 3, as cited in Armstrong (2015 survey), footnote 33 and surrounding text; abstract | That the profit-maximizing tariff leaves some buyers out of every market when private tastes are multidimensional | How large the excluded share is in any real market; whether excluded buyers value the goods above cost in practice; anything about competitive markets |
| Assumptions behind exclusion | Gross utility convex and homogeneous of degree one in taste parameters | Armstrong (2015 survey), footnote 33 | The conditions under which the exclusion argument goes through | That the result holds when these fail; the survey's own example with a different utility form has no exclusion |
| Cost-based tariff | Qualitative: payment depends on the bundle only through its cost | Armstrong (1996), abstract; class of explicit solutions | The form of the optimal tariff in the solvable cases | That real tariffs should be cost-based outside those cases, or that observed cost-plus pricing is evidence of optimal screening |
| Solvable example | Optimal tariff depends only on total quantity when the scale and relative-taste parameters are independent | Armstrong (1996), section 4.4, as described in Armstrong (2015 survey), section 3.2 | A special case where the multiproduct problem collapses to a one-dimensional one | Behavior when the two taste parameters are correlated; the survey says no such case was solved analytically |
| Rochet–Choné regions | Three regions: excluded, bunched, separated | Rochet and Choné (1998), section 7.2, as described in Armstrong (2015 survey) | The shape of the optimal allocation in one numerically solved example | Shares of buyers in each region (not reported in the sources I read); generality beyond the example |
| Manelli–Vincent optimal menu (later work) | Either good at 2/3, both at (4 − √2)/3, for two goods with values uniform on [0, 1] and zero cost | Daskalakis, Deckelbaum and Tzamos (2017), Example 1, restating Manelli and Vincent (2006) | The optimal deterministic menu in the simplest two-good case, which excludes a positive share of buyers as Armstrong predicts | Anything about Armstrong's own examples; this is a later paper's result |

## Interpretation notes

The exclusion result is a statement about the shape of an optimum, not a magnitude. It says the excluded set has
positive measure. It does not say the set is large, and the argument that proves it (a first-order gain against a
higher-order loss) works only in a neighborhood of zero exclusion. A reader who takes away "multiproduct sellers
exclude many buyers" has read more into it than the theorem supports.

The cost-based-tariff result belongs to a specific solvable class. Its practical appeal is that cost-plus pricing
plus an entry fee is easy to run, and Armstrong's survey links it to later results showing that with many products a
two-part tariff with prices near cost is approximately optimal (Armstrong 1999) and that a two-part tariff with
prices at marginal cost is an equilibrium under some forms of competition (Armstrong and Vickers 2001; Rochet and
Stole 2002). These are separate papers with their own assumptions, and the 1996 result should not be credited with
them.

Both papers assume a single seller who knows the distribution of tastes and commits to a tariff. Neither
addresses entry, rival sellers, or buyers who can resell. Those omissions are standard for the literature and are
stated as modeling choices rather than hidden.

## Unanswered questions

- How large is the excluded share in Armstrong's own examples, and how does it change with the number of products?
  The sources I read do not report a number.
- How sensitive is the exclusion result to the homogeneity assumption? The survey notes that a utility specification
  without it produces no exclusion, which suggests the result depends on how tastes enter utility.
- In Rochet and Choné's example, what share of buyers sits in each region, and how much profit would a simpler menu
  forgo?
- Do the predictions survive competition? The later work cited above suggests the cost-based form does, under
  independence assumptions, but exclusion under competition is a different question.

## Items requiring expert verification

- The precise statement of the exclusion theorem in section 3 of Armstrong (1996), including any conditions on the
  support of the type distribution (for example, whether the support must include points arbitrarily close to the
  zero-value corner, and whether the type set must be convex).
- Whether the paper's explicitly solved cases include any numerical example with reported profit or exclusion
  figures; I found none quoted in the secondary sources.
- The exact definition of "cost-based" used in the paper (a function of total cost, or cost plus a constant markup).
- The numerical method and grid used by Rochet and Choné in section 7.2, and whether their reported regions are
  robust to the discretization.

No published correction or comment documenting an analytical error in either paper was found. The points above are
reporting gaps in what I was able to read, not identified errors.

The modern rerun in this repository does not reproduce either paper, which have no data to reproduce. It takes the
two qualitative predictions, cost-based pricing with an entry fee and the exclusion of low-value buyers, and asks
how closely the published accounts of American warehouse clubs match them.
