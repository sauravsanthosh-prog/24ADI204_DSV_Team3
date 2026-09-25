# Week 4 findings

These are descriptive associations in the supplied Kaggle-derived file, not causal effects or predictions.

## Data quality

The raw file has 74,610 rows and 24 columns. Removing 112 exact duplicates leaves 74,498 unique employee IDs. The raw file has 4,325 missing cells; after deduplication, 1,897 distance and 2,381 company-tenure entries need imputation. Baseline imputation preserves missingness flags.

There are 35,370 Left labels (47.48%) and 39,128 Stayed labels. This is the observed left share, not an annual turnover rate.

## Evidence comparisons

| Comparison (exposed vs reference) | Difference, pp | 95% interval, pp | Cleaning swing, pp | Status |
|---|---:|---:|---:|---|
| Overtime | 5.96 | 5.20 to 6.73 | 0.19 | Robust descriptive signal |
| Limited remote access | 28.12 | 27.30 to 28.93 | 0.10 | Robust descriptive signal |
| Poor or fair balance | 19.54 | 18.83 to 20.24 | 0.40 | Robust descriptive signal |
| Low satisfaction | 5.89 | 4.70 to 7.09 | 0.47 | Robust descriptive signal |
| Low recognition | 0.56 | -0.17 to 1.29 | 0.15 | Needs caution |
| No promotions | 3.59 | 2.87 to 4.31 | 0.25 | Needs caution |
| Long commute (50+ recorded units) | 10.13 | 9.42 to 10.85 | 0.37 | Robust descriptive signal |

References: Overtime Yes vs No; Remote Work No vs Yes; balance Poor/Fair vs Good/Excellent; satisfaction Low vs other levels; recognition Low vs other levels; zero promotions vs one or more; distance >=50 vs <50 recorded units. A positive difference means the first group has a higher observed left share.

## Interpretation

- Non-remote records and poor/fair work-life balance show the largest gaps among the selected comparisons. Their directions persist across the tested cleaning scenarios and job roles. Follow-up questions are justified; guaranteed effects of changing policies are not.
- Overtime has a smaller but consistent gap. Review it together with work-life balance rather than declaring it the sole explanation.
- Low recognition is weak: its difference interval crosses zero and its direction is not consistent across all roles.
- Zero promotions has a positive gap, but it is below the declared 5-percentage-point practical threshold. A large sample can make a small gap statistically precise without making it operationally important.
- Satisfaction is non-monotonic: the Very High category also has a high left share. Do not summarize this as a simple downward trend.
- Income capping lowers the mean from about 7,344.88 to 7,302.05 recorded units while leaving the median at 7,348. Its unchanged categorical gaps are expected, not extra proof.

## Open quality issues

17,824 records imply employment starting before age 14; 66,049 observed tenure pairs disagree by more than 12 months under the assumption that the fields share a definition. They are flags for clarification, not established errors. 151 incomes are outside IQR fences. No source correction is invented.

## Limits and handoff

The dataset source is [Nikhil Bhosle on Kaggle](https://www.kaggle.com/datasets/nikhilbhosle/employee-attrition-uncleaned-dataset). Its sampling process, time period and original real/synthetic status remain unverified. Independence assumptions and exploratory comparisons limit interval interpretation. The evidence gate is a transparent project heuristic, not a validated decision rule.

The four original notebooks provide reproducible EDA code, outputs and explanations. Read [Week 4](../Source_Code/Notebooks/04_Week4_EDA_Book.ipynb), [methods](../Docs/METHODOLOGY.md) and [novelty](../Docs/NOVELTY.md).

## Weeks 5–9 completion

Nine executed notebooks now cover review preparation, transformations, PCA, dashboard and
final submission. The income Yeo–Johnson transform reduces skew from 5.208 to 0.038.
There are 40 encoded features; the pairwise correlation screen removes no further columns.
PCA retains 90.10% of variance in 24 components, with 22.24% in the first two. Standardizing
all encoded columns instead requires 30 components for 90%, showing weighting sensitivity.

The Streamlit dashboard provides six narrative chapters and eight plot types. Fourteen
automated tests passed. Project_Report.pdf and Final_Presentation.pptx cover the completed
workflow. PCA is unsupervised; no attrition classifier or prediction accuracy is claimed.
Weekly logs remain notebook Markdown. Human reviews and the actual expo/viva are team tasks.
