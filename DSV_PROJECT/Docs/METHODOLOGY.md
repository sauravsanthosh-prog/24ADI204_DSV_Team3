# Methods and cleaning decisions

## Reproducibility

The original CSV is immutable. `Source_Code/attrition_lab.py` is the shared implementation
used by the Week 1–4 audit notebooks. The manifest records its SHA-256 and derived counts. The notebooks
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

## Weeks 6–7: transformations and PCA

advanced_analysis.py selects six numeric and fifteen categorical source fields. ID, both
outcome representations, the ambiguous months-tenure field and audit flags are excluded.
For numeric fields with absolute skew above 1 and more than two values, Yeo–Johnson is
retained only if it reduces absolute skew. Income is the only selected transform in this
run: skew 5.208 to 0.038. Numeric fields are then standardized. MinMax is a separate
range-scaling comparison and does not claim to change skewness.

All categories are one-hot encoded, dropping the first sorted reference per field. Ordinal
labels are also one-hot encoded because equal spacing is not established. Dummies stay 0/1
in the primary matrix. This weighting favors unit-variance numeric fields relative to
individual dummy columns. An alternative fit standardizing every encoded column is reported.

After constant and pairwise |Pearson r| > 0.90 screening, all 40 encoded columns remain.
The fixed column order controls tie-breaking; the screen never consults Attrition. It does
not prove the absence of higher-order multicollinearity. Full-SVD PCA is fitted on the full
baseline for description. The minimum 24 components reaching 90% retain 90.10%; the first
two retain 22.24%. All-column standardization needs 30 components for 90%. Reconstruction
residuals independently verify retained variance. Component signs are arbitrary.

Dataset/Processed stores a compressed feature matrix and 24 scores. IDs are separate
row-alignment metadata; they are not PCA input columns. Outcome is attached only to the
display coordinates. There is no attrition classifier or independent predictive evaluation.

## Week 8: dashboard scope and sampling

The six-chapter Streamlit dashboard labels full-cohort audit/evidence views explicitly.
Explore-group role/age filters operate after each full-data cleaning scenario, and group
rates/intervals use the resulting cohort. These filtered charts do not inherit the global
evidence gate status. PCA filters select displayed records without refitting the basis.
Scatterplots use fixed seeds and state their sample sizes; aggregate tables use all eligible
records. Empty cohorts are handled. No ID is exposed in chart tooltips.

Official references: [PowerTransformer](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.PowerTransformer.html),
[OneHotEncoder](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.OneHotEncoder.html),
[PCA](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html),
[Streamlit testing](https://docs.streamlit.io/develop/api-reference/app-testing).
