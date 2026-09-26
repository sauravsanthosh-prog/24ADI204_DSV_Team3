# Employee Attrition Evidence Lab

**24ADI204 · Data Science and Visualization · Team No. 3 · Weeks 1–9**

A reproducible workflow: source audit, cleaning, EDA, evidence checks, feature engineering,
PCA and an interactive Streamlit dashboard. The original source CSV remains unchanged.

## Open these first

- [Project_Report.pdf](Project_Report.pdf): nine-page business insight report.
- [Final_Presentation.pptx](Final_Presentation.pptx): completed course-template slides.
- [File guide](Docs/FILE_GUIDE.md): what each saved file contains.
- [Demo and viva guide](Docs/DEMO_AND_VIVA.md): speaking sequence and answers.
- [Weekly coverage](Docs/WEEKLY_COMPLETION.md): milestone-to-deliverable mapping.

## Run in VS Code on Windows

Open **DSV_PROJECT** as the workspace. Install Python 3.12+ and the VS Code Python/Jupyter
extensions. Use its terminal:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run Source_Code/dashboard.py
```

Streamlit prints the local dashboard address, normally localhost:8501. After environment
setup, Start_Dashboard.ps1 also launches the app. No cloud account is required.
For notebooks, select **Select Kernel → Python Environments → .venv**, then **Run All**.
All nine notebooks include executed outputs and explanatory Markdown.

## Weekly logs and notebooks

| Week | Content |
|---|---|
| [Week 1 log](Source_Code/Notebooks/01_Week1_Project_and_Data_Source.ipynb) | Project question, data source and Pandas/NumPy setup |
| [Week 2 log](Source_Code/Notebooks/02_Week2_Know_Your_Data.ipynb) | Structure, types, missingness and first-impression quality report |
| [Week 3 log](Source_Code/Notebooks/03_Week3_Cleaning_Sprint.ipynb) | Cleaning, imputation alternatives and outlier flags |
| [Week 4 log](Source_Code/Notebooks/04_Week4_EDA_Book.ipynb) | EDA book, distributions and evidence scorecard |
| [Week 5 log](Source_Code/Notebooks/05_Week5_Data_Audit_Review.ipynb) | Consolidated data-audit review |
| [Week 6 log](Source_Code/Notebooks/06_Week6_Feature_Engineering.ipynb) | Feature exclusions, transformations, scaling and encoding |
| [Week 7 log](Source_Code/Notebooks/07_Week7_Feature_Selection_and_PCA.ipynb) | Correlation screen, PCA variance, coefficients and weighting sensitivity |
| [Week 8 log](Source_Code/Notebooks/08_Week8_Narrative_Dashboard.ipynb) | Dashboard narrative, interaction rules and app checks |
| [Week 9 log](Source_Code/Notebooks/09_Week9_Final_Submission_and_Viva.ipynb) | Submission inventory, validation results and viva preparation |

Each weekly log is an executed notebook containing explanatory Markdown, code and results. Click a week above to open it directly on GitHub.

## Regenerate and validate

Run from DSV_PROJECT:

```powershell
.\.venv\Scripts\python.exe Source_Code/attrition_lab.py
.\.venv\Scripts\python.exe Source_Code/advanced_analysis.py
.\.venv\Scripts\python.exe Source_Code/validate_project.py
.\.venv\Scripts\python.exe Source_Code/create_final_report.py
.\.venv\Scripts\python.exe Source_Code/run_notebooks.py
```

The shipped figures support report regeneration. Weeks 1–4 notebooks refresh their figures;
advanced_analysis.py refreshes Week 6–7 figures. The screenshot illustrates the tested app.
The last validation ran **14 tests with zero failures/errors**; all nine notebooks executed.
requirements-lock.txt records the exact tested environment.

## Measured results

- Raw **74,610 × 24**; **112** exact duplicates; **4,325** raw missing cells.
- Cleaned: **74,498** unique IDs; **35,370 Left**, **39,128 Stayed**; Left share **47.48%**.
- Largest selected gaps: non-remote **+28.12 pp**, poor/fair balance **+19.54 pp**.
- Income skew: **5.208 → 0.038** with Yeo–Johnson, then standardization.
- **40** encoded columns; no additional columns exceed the |r| > 0.90 screen.
- PCA: **24 components retain 90.10%**; first two retain **22.24%**.
- Standardizing all encoded columns instead needs **30 PCs** for 90%; weighting matters.

PCA is an unsupervised model of feature variance. There is **no attrition classifier or
measured predictive accuracy**. Shares are not annual rates; gaps are not causal effects;
PCA variance retention is not accuracy.

## What is distinctive?

Every selected EDA claim carries group sizes, uncertainty, five cleaning scenarios,
within-role comparisons and role/level standardization. The evidence gate explains why a
result passes the stated checks or needs caution. This is a distinctive integrated student
workflow, not a world-first method or a validated HR decision rule.

## Source and submission

Source: [Nikhil Bhosle on Kaggle](https://www.kaggle.com/datasets/nikhilbhosle/employee-attrition-uncleaned-dataset).
Sampling, dates, units and real/synthetic origin remain unverified. See Docs/METHODOLOGY.md
and Docs/DATA_DICTIONARY.md. The raw file is immutable.

Code and materials cover Weeks 1–9. Human peer review, faculty presentation, expo, viva and
formal submission still require the team. The optional video is not included. Notebook
Markdown serves as the weekly log; no Word logs were created.

RAW/, WEEK 1/ and WEEK 2/ contain legacy IBM work. The current Team 3 project and weekly logs are in DSV_PROJECT/Source_Code/Notebooks.
