# Employee Attrition Evidence Lab

**24ADI204 · Data Science and Visualization · Batch 3 / Team 3 · Weeks 1–4**

A fresh employee-attrition project using the team-supplied **Employee Attrition Uncleaned Dataset**.
It explains which observed workforce patterns survive different cleaning choices, with an
auditable evidence scorecard beside the EDA. This submission contains no trained prediction model.

## Start here

1. [Week 1 — project and source](Source_Code/Notebooks/01_Week1_Project_and_Data_Source.ipynb)
2. [Week 2 — know your data](Source_Code/Notebooks/02_Week2_Know_Your_Data.ipynb)
3. [Week 3 — cleaning sprint](Source_Code/Notebooks/03_Week3_Cleaning_Sprint.ipynb)
4. [Week 4 — EDA book](Source_Code/Notebooks/04_Week4_EDA_Book.ipynb)

The notebooks include executed outputs, chart interpretations and cleaning decisions.
Read the [results](Reports/FINDINGS.md), [novelty comparison](Docs/NOVELTY.md),
[data dictionary](Docs/DATA_DICTIONARY.md) and [methodology](Docs/METHODOLOGY.md).

## Run in VS Code

Install Python 3.12 or newer and the VS Code Python and Jupyter extensions. Open **this
DSV_PROJECT folder**, then use a terminal inside it:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Open a notebook, select **Select Kernel → Python Environments → .venv**, then **Run All**.
Each notebook works independently. No absolute local file paths are embedded in the project.
If Python is installed under a different command, substitute that interpreter for `py -3.12`.

To regenerate the cleaned data and numerical reports without opening notebooks:

```powershell
.\.venv\Scripts\python.exe Source_Code\attrition_lab.py
```

To execute and save all notebooks, including their chart outputs:

```powershell
.\.venv\Scripts\python.exe Source_Code\run_notebooks.py
```

Run meaningful data and statistical checks:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s Source_Code/tests -v
```

## What is different?

Prediction and HR dashboards already exist. This project adds an **evidence check for each
descriptive claim**: sample sizes, uncertainty, five cleaning scenarios, within-role comparisons,
role-and-level standardization, and visible reasons to withhold a strong conclusion.
The claim is a distinctive, reproducible student implementation, not a world-first algorithm
or a verified absence of these capabilities from every service.

## Dataset and results

- Source: [Nikhil Bhosle on Kaggle](https://www.kaggle.com/datasets/nikhilbhosle/employee-attrition-uncleaned-dataset).
- Raw: **74,610 rows × 24 fields**; **112 exact duplicates**; **4,325 missing cells**.
- Baseline cleaned: **74,498 unique employee IDs**, with **35,370 Left** and **39,128 Stayed**.
- Observed left share: **47.48%**. It is **not an annual turnover rate**.
- Missing values are filled in two fields, with their missingness flags preserved.
- Unusual values and tenure-definition concerns are flagged, not silently removed.
- File identity, counts and thresholds: [run manifest](Reports/run_manifest.json).

The raw file is copied byte-for-byte from the supplied CSV. Data origin, sampling, currency,
distance units and collection period have not been independently verified. Faculty approval
was confirmed by the team. The Kaggle API reports the dataset license as “Other (specified
in description)”; no different dataset license is asserted here.

## Folder map

```text
DSV_PROJECT/
  Source_Code/
    Notebooks/       # Four executed weekly notebooks; Week 4 is the EDA book
    attrition_lab.py # Loading, quality reports, cleaning and evidence methods
    run_notebooks.py
    tests/
  Dataset/
    Raw/             # Immutable replacement CSV
    Cleaned/         # Baseline data plus explicit audit flags
  Reports/
    Figures/         # Exported charts
    FINDINGS.md
    *.csv            # Quality, outlier, summary and evidence tables
    run_manifest.json
  Docs/              # Novelty, source dictionary, decisions and viva notes
  .vscode/           # Recommended extensions and local environment setting
  requirements.txt
  requirements-lock.txt
```

## Earlier material in this repository

`RAW/`, `WEEK 1/` and `WEEK 2/` predate this restart and use the previous IBM dataset.
They are preserved as historical files and are **not** inputs or evidence for this submission.
The original Word logs and presentation have not been edited. Presentation model scores
were confirmed as placeholders and must not be cited as measured results.

## Scope and next weeks

Week 1: source and setup. Week 2: first-impression audit. Week 3: imputation and outlier
diagnostics. Week 4: univariate/bivariate EDA and the evidence prototype. Scaling, encoding,
PCA and dashboard construction belong to later scheduled weeks. No Word logs or revised
slides are included in this restart.

## GitHub workflow

The repository is `sauravsanthosh-prog/24ADI204_DSV_Team3`; the project lives in `DSV_PROJECT`.
Use VS Code's Source Control **Sync Changes** after GitHub sign-in, or `git push origin main`
from the repository if a local commit is ahead. Never put passwords or access tokens in notebooks.
Publication status should be checked on GitHub; the existence of local files is not proof of upload.
