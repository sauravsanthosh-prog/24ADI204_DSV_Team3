# Team 4: six-minute demo and viva guide

## Before the review

Open DSV_PROJECT in VS Code. Follow README.md to select the .venv kernel and start the
dashboard. Open Project_Report.pdf and Final_Presentation.pptx. Use the nine current
notebooks; the old RAW / WEEK 1 / WEEK 2 folders are historical IBM work.

## Demo sequence

1. **0:00–0:45, Overview:** “We built an employee attrition evidence workflow. The cleaned
   dataset has 74,498 records. The observed Left share is 47.48%, not an annual rate.”
2. **0:45–1:30, Data audit:** Show the 112 exact duplicates, missingness and the income
   transformation. Explain median imputation, flags, and why unusual rows remain visible.
3. **1:30–2:30, Explore groups:** Choose a role and a cleaning scenario. Show how the
   denominator changes. Demonstrate a histogram, box/violin, scatter and heatmap.
4. **2:30–3:45, Evidence checks:** Explain the remote-access and balance gaps. Show low
   recognition as a caution example. State that the scorecard uses the full cohort.
5. **3:45–4:45, PCA map:** 40 encoded features → 24 components → 90.10% retained variance.
   The first two PCs show 22.24%; outcome is used only for colour. Switch to 3D if useful.
6. **4:45–6:00, Next actions:** Clarify source definitions, investigate working conditions,
   and measure any policy pilot prospectively. Finish with limitations and reproducibility.

## Questions and answers

**What is your novelty?** Each descriptive claim carries sample sizes, an uncertainty
interval, five cleaning scenarios, role consistency and standardization, plus explicit
reasons for caution. It is a distinctive integrated workflow, not a world-first algorithm.

**Why median instead of mean?** Median is less sensitive to extreme observations. We preserve
missingness flags and compare group medians and complete cases; we do not assume the missingness
mechanism is solved.

**Why keep outliers?** A statistical extreme is not automatically a data error. We retain
the baseline and examine income capping as a separate scenario.

**Why are the missing counts different?** 4,325 is raw missing cells. After duplicate removal,
1,897 distance and 2,381 tenure-in-months cells require imputation (4,278 total).

**Did scaling remove skew?** No. Yeo–Johnson changed income skew from 5.208 to 0.038.
MinMax and StandardScaler only change units, center or scale.

**Why one-hot encode?** It avoids invented numeric distances between categories. One category
is dropped per field to avoid exact dummy redundancy. Reference categories are documented.

**What did feature selection remove?** IDs, outcomes, ambiguous months tenure and audit flags
are excluded explicitly. The |r| > 0.90 / constant screen removes no additional encoded
columns in this dataset. We do not invent deletions.

**Why 24 PCs?** It is the minimum number reaching 90% variance under the chosen weighting.
The reconstruction-residual check agrees with the explained-variance calculation.

**Is 90.10% your accuracy?** No. It is retained feature variance. No attrition classifier
or predictive accuracy is part of this project.

**Why not standardize all dummies?** That amplifies rare categories. Our primary analysis
standardizes numeric columns and leaves dummies at 0/1. Standardizing every column requires
30 PCs for 90%; the sensitivity is reported.

**Can remote work reduce attrition by 28.12%?** This is a 28.12 percentage-point observed gap,
not a measured policy effect. Role, selection and unmeasured factors can contribute.

**How was it tested?** 14 checks cover source integrity, imputation, statistical intervals,
target exclusion, scaling, PCA reconstruction, dashboard pages and filters. The report records
the actual run. Human peer review, attendance, and the viva are still team activities.

## Team roles confirmed for this project

| Member | Role |
|---|---|
| Rohith Varma (25BAD090) | Data engineering |
| Saurav Santhosh (25BAD104) | Data analysis |
| Sinan Ubaid (25BAD107) | Visualization |
| Nishanth (25BAD070) | Lead / storytelling |

Each member should understand the full workflow, especially the distinction between
observed differences, PCA variance and predictive accuracy.
