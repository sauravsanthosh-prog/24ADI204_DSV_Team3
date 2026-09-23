# Novelty and existing services

## Proposed contribution

**Employee Attrition Evidence Lab: an auditable check of whether an EDA claim survives
cleaning choices and workforce composition.**

The user wanted a project that differs from a standard attrition-prediction service. Our
deliverable is an evidence-focused workflow, implemented by Week 4. Each claim links to
the raw-data identity, cleaning policy, underlying counts, uncertainty and subgroup comparisons.
The output can explicitly say **Needs caution**, instead of forcing a ranked retention suggestion.

## Public feature comparison

Reviewed 23 September 2026. These are vendor descriptions, not hands-on product evaluations.

| Reference | What the public page describes | Implication for this project |
|---|---|---|
| [Workday employee retention](https://www.workday.com/en-us/products/employee-voice/employee-retention.html) | Forecasting attrition and analysing employee experience | Prediction alone is not distinctive |
| [Visier talent retention](https://www.visier.com/products/talent-retention/) | Investigating attrition drivers and retention | Driver charts alone are not distinctive |
| This Week 4 prototype | Re-execute the same declared contrasts across five cleaning policies; expose counts, intervals, subgroup direction and rejection reasons | Focus the demonstration on transparent claim checking |

Public pages do not establish that these products lack similar internal methods. No exhaustive
market or patent search was performed. Do not describe the project as the first system ever
to use uncertainty, subgroup analysis or sensitivity checks. The novelty is the integrated,
reproducible workflow and demonstration on this supplied dataset.

## The feature reviewers can actually run

1. Open Week 4, section 7. Read the exact exposed/reference group definitions.
2. Inspect the unadjusted differences and their 95% intervals.
3. Inspect how each difference changes across median, group-median, complete-case,
   early-start exclusion and income-capping scenarios.
4. Compare signs in all five job roles and the role-level standardized estimate.
5. Read the scorecard's status and reason. Recognition is a useful caution example.
6. Change the displayed thresholds and rerun the evidence cells. A threshold is a visible
   judgement, not hidden logic masquerading as a scientific standard.

The baseline thresholds require 200 observations in each arm, an absolute gap of at least
5 percentage points in every scenario, intervals excluding zero, a common direction in
all roles/scenarios, a maximum 2-point cleaning swing, and an adjusted gap of at least
5 points with at least 90% population coverage. Passing is not causal validation.

## Later extension

A dashboard can let reviewers select an assumption and watch the claim and its evidence
change together. Budget simulations or proposed interventions would need explicit assumptions
and separate evidence about their effects. There are no invented savings or prevention claims
in the Week 4 prototype.

## Suggested viva description

“Our project checks how trustworthy an attrition insight is before presenting it. We attach
sample sizes and uncertainty, rerun the comparison under different cleaning choices, and
check job-role composition. The distinctive feature is that weak claims remain visible with
reasons for caution. We analyse associations; we do not claim to prove why employees leave.”
