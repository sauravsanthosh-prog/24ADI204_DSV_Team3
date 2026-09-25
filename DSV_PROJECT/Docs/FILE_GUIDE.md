# Current project files: what each contains

## Deliverables

| File or folder | Contents and use |
|---|---|
| Project_Report.pdf | Nine-page business insight report: source, cleaning, EDA, novelty, transformations, PCA, dashboard, actions and references. |
| Final_Presentation.pptx | Completed course-template slides for Team 4; presenter notes explain limitations. |
| README.md | Installation, VS Code, regeneration and dashboard launch instructions. |
| Start_Dashboard.ps1 | Windows shortcut to launch Streamlit using the project's .venv. |
| requirements.txt | Direct package requirements with compatible bounds. |
| requirements-lock.txt | Exact versions in the tested environment. |
| .vscode/ | Python/Jupyter recommendations and environment setting. |
| .streamlit/config.toml | Dashboard theme and telemetry preference. |

## Nine notebooks in Source_Code/Notebooks

| Week | File content |
|---|---|
| 1 | Project question, source provenance, Pandas/NumPy setup and dataset inspection. |
| 2 | Dtypes, shape, missingness and first-impression quality report. |
| 3 | Cleaning rationale, imputation alternatives, outlier and semantic flags. |
| 4 | The EDA book: distributions, comparisons, uncertainty and the evidence scorecard. |
| 5 | Consolidated data-audit review and initial statistical findings. |
| 6 | Exclusions, Yeo–Johnson, StandardScaler/MinMax and one-hot encoding. |
| 7 | Correlation screen, PCA variance, coefficients, projection and weighting sensitivity. |
| 8 | Dashboard narrative, interaction rules, plot inventory and live app checks. |
| 9 | Submission inventory, actual test results, demo and viva preparation. |

All notebooks contain executed outputs and explanatory Markdown. Each locates the project
relative to its folder; no machine-specific paths are embedded.

## Python scripts

| Script | Responsibility |
|---|---|
| attrition_lab.py | Load the original CSV, audit, clean, calculate intervals and generate EDA tables. |
| advanced_analysis.py | Transform, encode, select, run PCA and export Week 6–7 figures/data. |
| dashboard.py | Six interactive Streamlit story chapters. |
| run_notebooks.py | Execute all nine notebooks with the active Python environment. |
| validate_project.py | Run the 14 meaningful regression checks and save validation_results.json. |
| create_final_report.py | Regenerate the PDF from verified reports and figures. |
| tests/test_analysis.py | Row/label integrity, imputation and interval/gate behaviour. |
| tests/test_advanced.py | Target exclusion, scaling, correlation screen and PCA reconstruction. |
| tests/test_dashboard.py | Page rendering, cohort denominators, scenarios and empty/3D views. |

## Data and report artifacts

Dataset/Raw/Emp_attrition_csv.csv is the immutable supplied source. Dataset/Cleaned contains
the median-imputed baseline plus audit flags. Dataset/Processed/features_and_components.npz
contains the 40-column matrix, feature names, IDs for row alignment, and 24 retained PCA
scores; load with numpy.load(..., allow_pickle=False). IDs are metadata, not matrix columns.

Reports/data_quality_before.csv and data_quality_after.csv describe each field. The
outlier_audit.csv and row_quality_flags.csv retain diagnostic results. descriptive_statistics.csv
contains central tendency, dispersion, skewness and kurtosis.

evidence_scorecard.csv is the seven-comparison summary; cleaning_sensitivity.csv contains
all scenario comparisons; within_role_comparisons.csv contains role-specific gaps;
scenario_summary.csv and categorical_left_shares.csv provide supporting descriptive tables.

feature_transformations.csv records skew/lambda decisions; feature_scaling.csv contains
fitted centers/scales and checks; feature_encoding.csv records categories and references;
feature_exclusions.csv explains excluded source fields; feature_selection.csv logs every
encoded-column decision. encoded_correlation.csv is the full pairwise matrix.

pca_variance.csv gives component and cumulative variance, pca_loadings.csv component
coefficients, and pca_coordinates.csv the first three scores with row-alignment ID and
display-only outcome. advanced_manifest.json records dimensions, variance and weighting
sensitivity; run_manifest.json records the original audit. validation_results.json records
actual automated checks. Figures/ contains the 14 Week 2–4 charts, six Week 6–7 figures and
the dashboard screenshot.

## Documentation and historical files

DATA_DICTIONARY.md explains source fields; METHODOLOGY.md documents assumptions;
NOVELTY.md scopes the contribution; DEMO_AND_VIVA.md is the review speaking guide;
WEEKLY_COMPLETION.md maps requirements to deliverables.

RAW/, WEEK 1/ and WEEK 2/ use the older IBM dataset and are historical only. They are preserved
to avoid deleting earlier team work; they must not be presented as current analytical evidence.
