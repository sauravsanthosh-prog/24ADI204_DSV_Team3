# Data dictionary and source notes

Source supplied by the team: [Kaggle dataset](https://www.kaggle.com/datasets/nikhilbhosle/employee-attrition-uncleaned-dataset).
Definitions below describe the column names and observed values, not independently verified employer documentation.

| Field | Analytical type | Meaning / interpretation limit |
|---|---|---|
| Employee ID | Identifier | Audit key; excluded from explanatory statistics |
| Age | Numeric, integer | Age as recorded; interpreted as years from field context |
| Gender | Nominal | Recorded Male/Female categories; descriptive context only |
| Years at Company | Numeric, integer | Stated tenure in years; early-start consistency flags apply |
| Job Role | Nominal | Five sector-like labels; no finer occupation information |
| Monthly Income | Numeric | Currency unspecified; retain original units |
| Work-Life Balance | Ordinal | Poor, Fair, Good, Excellent |
| Job Satisfaction | Ordinal | Low, Medium, High, Very High |
| Performance Rating | Ordinal | Low, Below Average, Average, High |
| Number of Promotions | Discrete count | Observed 0–4; time window unspecified |
| Overtime | Binary category | Yes/No; overtime hours are absent |
| Distance from Home | Numeric | Unit unspecified; contains nulls |
| Education Level | Category | High School, Associate, Bachelor's, Master's, PhD; text repaired |
| Marital Status | Nominal | Single, Married, Divorced; descriptive context only |
| Number of Dependents | Discrete count | Values up to 15; unusual values flagged by audit |
| Job Level | Ordinal | Entry, Mid, Senior |
| Company Size | Ordinal | Small, Medium, Large; thresholds absent |
| Company Tenure (In Months) | Numeric | Name implies months; meaning conflicts with Years at Company |
| Remote Work | Binary category | Yes/No; arrangements and eligibility unspecified |
| Leadership Opportunities | Binary category | Yes/No; source definition unverified |
| Innovation Opportunities | Binary category | Yes/No; source definition unverified |
| Company Reputation | Ordinal | Poor, Fair, Good, Excellent |
| Employee Recognition | Ordinal | Low, Medium, High, Very High |
| Attrition | Outcome category | Stayed/Left; no observation period or exit reason |

## Derived fields in the cleaned file

`Left` is 1 for Left and 0 for Stayed. Two `... Missing` columns identify originally missing
distance and company-tenure values. `Early Start Flag` identifies Age − Years at Company < 14.
`Tenure Definition Review` marks a discrepancy over 12 months between apparently corresponding
tenure fields where observed. `Income IQR Flag` identifies incomes outside the original
deduplicated IQR fences. Flags are diagnostic and must not be treated as independent predictors
without a justified later design.

## Provenance and license

The raw copy is exactly the team-supplied `Emp_attrition_csv.csv`; its hash is in the manifest.
The team confirmed dataset approval. We have not independently established who originally
generated the records, whether they are synthetic, the population sampled, or the period covered.
The public Kaggle dataset-list API returned “Other (specified in description)” as its license.
Refer to the source for terms; no additional dataset license is asserted in this repository.
The source link does not make the old IBM-specific logs valid for the replacement data.
