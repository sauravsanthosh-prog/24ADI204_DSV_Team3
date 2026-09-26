"""Create the nine-page business insight report from verified saved results."""
from pathlib import Path
import json
from xml.sax.saxutils import escape
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,Image,PageBreak

ROOT=Path(__file__).resolve().parents[1]
FIG=ROOT/'Reports'/'Figures'
NAVY=colors.HexColor('#183247');TEAL=colors.HexColor('#147D92')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodyLab',fontName='Helvetica',fontSize=10.5,leading=15,spaceAfter=10,textColor=NAVY))
styles.add(ParagraphStyle(name='TitleLab',fontName='Helvetica-Bold',fontSize=27,leading=31,spaceAfter=15,textColor=NAVY))
styles.add(ParagraphStyle(name='HeadingLab',fontName='Helvetica-Bold',fontSize=17,leading=22,spaceAfter=13,textColor=TEAL))
styles.add(ParagraphStyle(name='SmallLab',fontName='Helvetica',fontSize=8.6,leading=11.5,spaceAfter=7,textColor=NAVY))
styles.add(ParagraphStyle(name='CellLab',fontName='Helvetica',fontSize=9,leading=12,textColor=NAVY))

def build():
    advanced=json.loads((ROOT/'Reports'/'advanced_manifest.json').read_text())
    validation=json.loads((ROOT/'Reports'/'validation_results.json').read_text())
    transforms=pd.read_csv(ROOT/'Reports'/'feature_transformations.csv')
    income=transforms.set_index('feature').loc['Monthly Income']
    score=pd.read_csv(ROOT/'Reports'/'evidence_scorecard.csv')
    story=[]
    def p(s,style='BodyLab'):story.append(Paragraph(s,styles[style]))
    def heading(number,title):
        if number>1:story.append(PageBreak())
        p(f'{number:02d} / BUSINESS INSIGHT REPORT','SmallLab');p(title,'TitleLab')
    def table(rows,widths):
        formatted=[[Paragraph(escape(str(v)),styles['CellLab']) for v in row] for row in rows]
        t=Table(formatted,colWidths=widths,repeatRows=1,hAlign='LEFT')
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E4F1F3')),
            ('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),1,TEAL),
            ('BOTTOMPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),8),
            ('LINEBELOW',(0,1),(-1,-1),.25,colors.HexColor('#D7E3E8'))]))
        story.extend([t,Spacer(1,12)])
    def image(name,w=490,maxh=275):
        im=Image(str(FIG/name));ratio=min(w/im.imageWidth,maxh/im.imageHeight)
        im.drawWidth=im.imageWidth*ratio;im.drawHeight=im.imageHeight*ratio
        story.extend([im,Spacer(1,10)])

    heading(1,'Employee Attrition<br/>Evidence Lab')
    p('Team No. 3 | 24ADI204 Data Science and Visualization<br/>Weeks 1-9 deliverables | 25 September 2026','HeadingLab')
    p('<b>Executive summary.</b> The project turns a messy employee dataset into an auditable visual story. It asks which observed workforce differences remain stable when cleaning assumptions and subgroup composition are examined. The deliverable combines reproducible notebooks, an evidence scorecard, feature transformations, PCA and a local interactive dashboard.')
    table([['Raw records','Cleaned records','Observed Left share'],['74,610','74,498','47.48%']], [163,163,164])
    p('<b>The main finding:</b> non-remote records have a 28.12 percentage-point higher observed Left share than remote records. Poor/fair work-life balance has a 19.54-point gap compared with good/excellent balance. Their directions persist across the specified cleaning and role checks. These results support further investigation; they do not quantify the effect of changing a policy.')
    p(f'<b>The analytical handoff:</b> the selected income transformation reduces skew from {income.raw_skew:.3f} to {income.selected_skew:.3f}. PCA reduces 40 encoded columns to {advanced["components_retained"]} components while retaining {advanced["retained_variance"]:.2%} of the matrix variance. The dashboard exposes the evidence and its limits through six narrative chapters.')
    p('<b>Recommended next step:</b> clarify source definitions, then investigate remote access and work-life balance with context from comparable roles and voluntary feedback. Evaluate any intervention prospectively. Do not use these descriptive results to label individual employees or promise a reduction in turnover.')
    p('This is a descriptive visualization project. No attrition classifier, causal effect estimate or measured prediction accuracy is included. The final expo and viva must be delivered by the team.','SmallLab')

    heading(2,'Data profile and provenance')
    p('The team supplied Emp_attrition_csv.csv and identified the Kaggle Employee Attrition Uncleaned Dataset by Nikhil Bhosle as its source. The raw file is preserved byte-for-byte. The replacement dataset is the sole input to current notebooks; historical IBM material in the repository is excluded.')
    table([['Item','Verified description'],['Structure','74,610 records; 24 original columns; structured CSV'],
        ['Outcome','Attrition: Left or Stayed; no missing labels'],['Baseline','74,498 rows after removing 112 exact duplicates; IDs are unique'],
        ['Label composition','35,370 Left; 39,128 Stayed'],['Missingness','4,325 missing cells in the raw data'],
        ['Original numeric fields','Age, years at company, income, promotions, distance, dependents and tenure in months']], [130,360])
    p('The observed Left share is a sample fraction. The file does not establish a reporting period or an at-risk population for annual turnover. We therefore avoid calling 47.48% an annual rate. Its two labels are fairly balanced, so severe class imbalance is not the central challenge here.')
    p('Sampling frame, collection dates, original employer, distance and income units, and real-versus-synthetic origin remain unverified. The team previously confirmed faculty approval of the dataset. That confirmation does not resolve the statistical provenance questions. The source license was reported as "Other (specified in description)"; no different license is asserted.')
    p('<b>Audit trail.</b> Reports/run_manifest.json and advanced_manifest.json record the raw-file SHA-256 and derived dimensions. This lets a reviewer distinguish a reproduced run from a calculation using a different CSV. Dataset/Raw remains unchanged while cleaned and transformed artifacts are stored separately.')
    p('Source: <link href="https://www.kaggle.com/datasets/nikhilbhosle/employee-attrition-uncleaned-dataset" color="#147D92">Kaggle dataset page</link>. Consult Docs/DATA_DICTIONARY.md for field-level notes.','SmallLab')

    heading(3,'Cleaning decisions and quality')
    p('Cleaning aims to preserve traceability. The pipeline removes full-row duplicates, checks that no conflicting IDs remain, strips surrounding text whitespace, and explicitly repairs two corrupted education labels. It never fills missing outcome labels or guesses a corrected value for an ambiguous field.')
    table([['Decision','Reason and recorded consequence'],['Median imputation','After deduplication, fill 1,897 distance and 2,381 tenure-in-months values. Keep a boolean flag for each missing field.'],
        ['Outlier handling','IQR and absolute z-score > 3 are diagnostic. Retain baseline outliers; 151 income values exceed IQR fences.'],
        ['Starting-age review','17,824 records imply starting before age 14 under age minus years-at-company. Flag for review; do not declare them established errors.'],
        ['Tenure definition review','66,049 observed pairs differ by more than 12 months if both fields mean the same thing. The meaning is unresolved.']], [135,355])
    p('Median imputation is a robust, simple baseline in the presence of extreme values. It does not establish that missingness is random and can compress the distribution near the median. The missingness flags retain this information for audit. Row counts before and after deduplication must not be mixed when explaining the number of imputed cells.')
    p('Five scenarios probe sensitivity: overall median, role/level median with overall fallback, complete cases, exclusion of early-start flags, and income IQR capping. These are alternatives, not five equally correct datasets. Complete-case and early-start scenarios change cohort membership, so every comparison carries its own denominator.')
    p('Income capping does not directly change the selected categorical or distance comparisons. Their invariance under that scenario is expected. The income mean changes while the median remains unchanged; that is the relevant consequence to inspect for that scenario.')

    heading(4,'Visual evidence: observed differences')
    p('The EDA covers distributions, central tendency, dispersion, skewness, kurtosis and bivariate relationships. The figure summarizes seven selected comparisons as differences in observed Left share. Each horizontal interval is a 95% Wilson-based difference interval; positive values mean the first group has a higher share.')
    image('04_evidence_scorecard.png',maxh=265)
    rows=[['Comparison','Gap (pp)','95% interval (pp)']]
    for _,r in score.iterrows():rows.append([r['contrast'],f'{r.difference_pp:.2f}',f'{r.ci_low_pp:.2f} to {r.ci_high_pp:.2f}'])
    table(rows,[270,75,145])
    p('Comparisons: non-remote versus remote; poor/fair versus good/excellent balance; distance >=50 versus <50 recorded units; overtime Yes versus No; low satisfaction/recognition versus other levels; zero versus at least one promotion. These are descriptive, unadjusted gaps. The next page explains the caution labels.','SmallLab')

    heading(5,'Novelty: making caution visible')
    p('The project contribution is an integrated evidence workflow beside the EDA. Prediction products and HR dashboards already exist. Here, a claim is accompanied by sample sizes, uncertainty, sensitivity to cleaning, within-role checks and role/level standardization. A reviewer can see why the workflow withholds a strong conclusion.')
    table([['Gate check','Declared threshold or condition'],['Sample size','At least 200 records in each comparison arm across scenarios and roles'],
        ['Magnitude','Absolute gap at least 5 percentage points across scenarios'],['Direction and interval','Same direction and interval excluding zero in every scenario'],
        ['Cleaning swing','Largest minus smallest difference no more than 2 points'],['Composition','Within-role direction stable; standardized gap retains direction and magnitude with at least 90% coverage']], [145,345])
    p('Low recognition has a 0.56-point gap with an interval crossing zero and inconsistent role directions. It therefore needs caution. No promotions has a positive 3.59-point gap but falls below the stated practical threshold. A large sample can produce a narrow interval for an effect that remains small by the chosen operational criterion.')
    p('Job satisfaction is not monotonic: the Very High category also shows a high Left share. It would be misleading to present satisfaction as a simple linear protective factor. This is an example of why detailed category plots matter alongside a collapsed comparison.')
    p('The gate is an explicit exploratory heuristic, not a validated decision rule or a multiple-testing-corrected significance claim. Intervals assume independent rows and cannot repair selection bias, clustering or unknown provenance. Standardization is descriptive adjustment for measured role and level; unmeasured confounding remains.')
    p('The novelty claim is a distinctive, reproducible student implementation. It is not a claim that the individual statistical methods are new or that no existing service offers similar checks.','SmallLab')

    heading(6,'Feature engineering: shape and scale')
    p('Twenty-one original fields enter the representation: six numeric and fifteen categorical. ID, both outcome representations, the ambiguous tenure-in-months field and five audit flags are excluded. Exclusions and reasons are saved. Labels are never used to choose the transformations.')
    image('06_income_transformations.png',maxh=200)
    p(f'Income is the only numeric field exceeding the stated absolute-skew trigger of 1. Yeo-Johnson reduces its skew from {income.raw_skew:.3f} to {income.selected_skew:.3f}; the fitted lambda is {income["lambda"]:.3f}. We retain the other numeric shapes. This improvement is a shape diagnostic, not a guarantee of Gaussian data or better prediction.')
    p('MinMax scaling maps a field to a bounded range using observed extrema. StandardScaler centers it and scales to unit population standard deviation. Both are linear changes and preserve skewness. The before/after figure therefore distinguishes MinMax-only scaling from the selected nonlinear transformation plus standardization.')
    p('One-hot encoding avoids assigning arbitrary distances to nominal categories. One reference category is dropped per field to avoid exact dummy redundancy. We also one-hot encode ordered categories because equal spacing between their levels is not established. The resulting matrix has 40 columns. The encoding report records every reference category.')
    p('Numeric columns receive unit variance while dummy columns remain 0/1. This primary weighting is deliberate and affects PCA geometry. An alternative fit standardizes all encoded columns and is reported as a sensitivity check. All fits here use the full cohort for description. A future classifier must split data first and fit preprocessing on training data only.')

    heading(7,'PCA: measured compression')
    p('The pairwise correlation screen removes constants and later columns with |Pearson r| > 0.90 against an already retained column. It removes zero further columns on this dataset. We report that outcome honestly; reference-category dropping has already addressed exact dummy redundancy. The screen is not proof that all multicollinearity is absent.')
    image('07_explained_variance.png',maxh=185)
    p(f'Full-SVD PCA retains {advanced["retained_variance"]:.2%} of the matrix variance using {advanced["components_retained"]} of 40 components. The component count is the smallest that reaches the 90% target. A reconstruction-residual calculation independently verifies the retained-variance result.')
    image('07_pca_scatter.png',maxh=220)
    p(f'The first two components retain only {advanced["first_two_variance"]:.2%}; the scatterplot is therefore a partial view. It displays a fixed sample of 4,000 records, with outcome colours added after fitting. It does not establish predictive separation. Standardizing all encoded columns requires {advanced["all_columns_standardized_components_90"]} components for 90%, demonstrating sensitivity to weighting.','SmallLab')

    heading(8,'The narrative dashboard and validation')
    p('The Streamlit/Plotly dashboard is a local application with six chapters. Overview establishes context; Data audit exposes the conflict; Explore groups invites comparison; Evidence checks explains which claims survive; PCA map shows structure; Next actions states the follow-up questions.')
    image('08_dashboard_overview.png',maxh=255)
    p('Eight plot types are available: bar, histogram, box, violin, scatter, heatmap, line and 3D scatter. Role, age and cleaning-scenario controls recalculate the exploration cohort. Empty selections produce a clear message. Aggregate group and evidence tables can be downloaded as CSV for review.')
    p('Scope is explicit. Evidence status remains a full-cohort result and is labelled accordingly. PCA filters change which records are displayed, not the fitted basis. Large scatterplots state their fixed sample size; aggregate plots use all eligible cohort records. Employee IDs are not included in chart tooltips.')
    p(f'<b>Validation:</b> {validation["tests_run"]} automated tests ran with {validation["failures"]} failures and {validation["errors"]} errors. Checks cover data accounting, unchanged observed values, target-independent transforms, pairwise screening, scaling, PCA orthogonality/reconstruction, all six chapters, alternate scenarios, violin/3D views and empty selections. Browser inspection also confirms the dashboard loads and renders. These checks do not substitute for a live faculty demo or human peer review.')
    p('Launch: create the project .venv, install requirements.txt, then run python -m streamlit run Source_Code/dashboard.py. See README.md for exact Windows commands.','SmallLab')

    heading(9,'Conclusion and handover')
    p('The completed workflow supports a defensible conversation about observed attrition patterns. Remote access and work-life balance deserve deeper investigation; low recognition and no promotions demonstrate why caution should remain visible. Transformations and PCA extend the analysis without converting association into prediction or causation.')
    table([['Action','Evidence boundary'],['Clarify source definitions','Resolve dates, sampling, units and tenure meanings before external application.'],
        ['Investigate working conditions','Use comparable roles and voluntary contextual feedback to understand remote/balance differences.'],
        ['Evaluate a policy pilot','Define outcomes and a comparison prospectively; measure the pilot instead of promising dataset gaps as effects.'],
        ['Present and defend','Run the six-chapter demo and explain cleaning, thresholds, PCA variance and limitations.']], [150,340])
    p('<b>Team responsibilities:</b> Rohith Varma (25BAD090): data engineering; Saurav Santhosh (25BAD104): analysis; Sinan Ubaid (25BAD107): visualization; Nishanth (25BAD070): lead/storytelling. These are the team roles confirmed for Team No. 3. They do not claim a verified per-file authorship history.')
    p('<b>Handover:</b> nine executed notebooks, raw/cleaned/processed data, analysis scripts, dashboard, chart and CSV reports, this report, a final presentation, a file guide and a viva/demo guide. The optional video is not included. Week 5 and Week 9 review materials are prepared; the team must attend and deliver the actual reviews.')
    p('<b>References and reproducibility</b>','HeadingLab')
    for s in [
        'Nikhil Bhosle. Employee Attrition Uncleaned Dataset. <link href="https://www.kaggle.com/datasets/nikhilbhosle/employee-attrition-uncleaned-dataset" color="#147D92">Kaggle source</link>.',
        'Faculty-supplied DSV Rule Book, DATA-VIZ HACK-A-BIT 2026-2027, 24ADI204, pp. 1-5.',
        'Scikit-learn: <link href="https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.PowerTransformer.html" color="#147D92">PowerTransformer</link>, <link href="https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.OneHotEncoder.html" color="#147D92">OneHotEncoder</link> and <link href="https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html" color="#147D92">PCA</link> documentation (accessed 25 September 2026).',
        'Streamlit: <link href="https://docs.streamlit.io/develop/api-reference/app-testing" color="#147D92">App testing documentation</link>. Newcombe (1998), Statistics in Medicine 17, 873-890; interval method details in Docs/METHODOLOGY.md.',
        '<link href="https://github.com/sauravsanthosh-prog/24ADI204_DSV_Team3/tree/main/DSV_PROJECT" color="#147D92">Project repository</link>. Team 3 project source and weekly notebooks.'
    ]:p(s,'SmallLab')
    def footer(canvas,doc):
        canvas.saveState();canvas.setStrokeColor(TEAL);canvas.line(48,42,547,42)
        canvas.setFont('Helvetica',8);canvas.setFillColor(NAVY)
        canvas.drawString(48,28,'TEAM 3 | EMPLOYEE ATTRITION EVIDENCE LAB')
        canvas.drawRightString(547,28,f'{doc.page} / 9');canvas.restoreState()
    doc=SimpleDocTemplate(str(ROOT/'Project_Report.pdf'),pagesize=A4,leftMargin=48,rightMargin=48,topMargin=42,bottomMargin=57,
        title='Employee Attrition Evidence Lab | Team 3',author='Team 3')
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    print(ROOT/'Project_Report.pdf')

if __name__=='__main__':build()
