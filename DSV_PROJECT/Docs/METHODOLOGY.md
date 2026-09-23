# Methods and cleaning decisions

## Reproducibility

The original CSV is immutable. `Source_Code/attrition_lab.py` is the shared implementation
used by all four notebooks. The manifest records its SHA-256 and derived counts. The notebooks
contain their own loading cells, so no hidden execution order between weeks is required.
The scatterplot sample uses seed 42; aggregate analyses use all eligible records.

## Baseline cleaning

Remove only full-row duplicates. If IDs still repeat, raise an error for review instead of
arbitrarily keeping a conflicting employee record. Strip surrounding whitespace and repair
the two observed education-label encoding errors. Missing distance and company-tenure values
receive the corresponding global median, and boolean missingness flags preserve their origin.
Imputation uses no target values. Attrition labels and observed incomes remain unchanged.

Median is a simple robust baseline, not a claim about the missingness mechanism. Group-median
imputation uses Job Role and Job Level, with global-median fallback for empty groups.
Complete-case analysis excludes rows missing either of the two fields after deduplication.
The comparison cohorts can therefore differ; report their denominators explicitly.

## Outlier and semantic audits

IQR and |Z| > 3 are calculated for all seven numeric fields excluding the ID. Z uses ddof=0.
An IQR or Z flag alone does not justify deleting plausible employees. The baseline retains
extreme incomes and unusual counts. A separate income-capping scenario clips to IQR fences.

An implied start age below 14 is a plausibility assumption for sensitivity, not a legal rule.
Tenure disagreement is |12 × Years at Company − Company Tenure (In Months)| > 12 where both
are observed. The latter check is conditional on comparable meanings; definitions are unresolved.
Missing tenure does not count as agreement: inspect the separate missing flag. Do not
replace one tenure variable with the other or use these concerns to delete most of the data.

## Descriptive statistics and visual analysis

Count, mean, median, sample variance/std, quartiles, min/max, skewness and excess kurtosis are
exported. Ordered categories use their semantic order. Histograms, bars, boxplots, violin plots,
scatterplots and heatmaps cover univariate and bivariate EDA. Spearman correlation excludes
Employee ID and the ambiguous company-tenure-in-months field; age/years plots are diagnostic.
Left share is a sample fraction, not an annual rate. No currency or distance unit is invented.

## Evidence scorecard

Each contrast is defined in `CONTRASTS`. The difference is exposed left share minus reference
left share, in percentage points. A Wilson interval describes each binomial share. Differences
use the Newcombe Wilson-based interval for independent groups, with no continuity correction.
The minimum-group threshold applies to each arm in every scenario and in each reported role.

Direct standardization averages within role × level differences weighted by the population
of each eligible stratum. Both arms must contain at least 200 records; excluded strata reduce
the reported coverage. No adjusted interval or full causal control is claimed. The gate requires
the adjusted difference to retain direction and practical magnitude with at least 90% coverage.

Default thresholds are stated in the novelty note and editable in Week 4. The saved CSV reports
use default thresholds; changing notebook thresholds changes the displayed scorecard, not the
default report files unless the analyst explicitly exports them. The notebook's status is not
a multiple-testing-corrected significance claim. Analysis is exploratory and not preregistered.

Income capping has no direct effect on the selected categorical or commute contrasts. This
expected invariance is reported, not sold as extra independent evidence. Its effect on the
income mean is shown separately in the scenario summary. Commute is directly sensitive to
imputation. Early-start exclusion tests sensitivity to one semantic concern; it cannot cure
unknown data provenance or unmeasured confounding.

## Interpretation limits

Unknown collection process, temporal window, company clusters and synthetic/real origin limit
generalization. Confidence intervals assume independent rows and do not repair selection bias.
No prediction model, individual score, fairness certification or causal treatment effect is
estimated. If future modelling is added, split before fitting any preprocessing and reserve
an untouched evaluation set. EDA on this full dataset is not independent model evaluation.

## Reference for interval methods

Newcombe, R. G. (1998). Interval estimation for the difference between independent proportions:
comparison of eleven methods. *Statistics in Medicine*, 17, 873–890.
[DOI](https://doi.org/10.1002/(SICI)1097-0258(19980430)17:8%3C873::AID-SIM779%3E3.0.CO;2-I).
