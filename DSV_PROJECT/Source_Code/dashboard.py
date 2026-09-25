"""Week 8 narrative dashboard. Run: streamlit run Source_Code/dashboard.py"""
import json
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from attrition_lab import ROOT, NUMERIC, load_raw, clean_data, rate_table, scenarios, CONTRASTS

st.set_page_config(page_title='Attrition Evidence Lab | Team 4',page_icon='📊',layout='wide')
COLOURS={'Stayed':'#147D92','Left':'#E57B55'}

@st.cache_data
def dataset():
    raw=load_raw()
    return raw,clean_data(raw)

@st.cache_data
def scenario_data(name):
    raw=load_raw()
    if name=='Median / retain flags':return clean_data(raw)
    if name=='Role-level median':return clean_data(raw,'group_median')
    if name=='Complete case':return clean_data(raw,'complete_case')
    base=clean_data(raw)
    if name=='Exclude early-start flags':return base.loc[~base['Early Start Flag']].copy()
    q1,q3=base['Monthly Income'].quantile([.25,.75])
    base['Monthly Income']=base['Monthly Income'].clip(q1-1.5*(q3-q1),q3+1.5*(q3-q1))
    return base

def chart(fig):
    fig.update_layout(template='plotly_white',font={'family':'Arial','size':14},
        margin={'l':15,'r':15,'t':55,'b':35},legend_title_text='')
    st.plotly_chart(fig,width='stretch')

def read(name):return pd.read_csv(ROOT/'Reports'/name)

def filter_cohort(data,roles,age):
    return data.loc[data['Job Role'].isin(roles)&data.Age.between(*age)].copy()

def main():
    raw,base=dataset()
    st.sidebar.title('Evidence Lab')
    st.sidebar.caption('Team 4 · 24ADI204 · Weeks 1–9')
    page=st.sidebar.radio('Story chapter',['Overview','Data audit','Explore groups','Evidence checks','PCA map','Next actions'],key='page')
    st.sidebar.divider()
    st.sidebar.caption('Source: Kaggle employee attrition uncleaned dataset. Observed sample shares; no individual risk scores.')
    st.title('Employee Attrition Evidence Lab')
    st.caption('Context → data quality → patterns → evidence checks → responsible next steps')
    if page=='Overview':
        st.header('Where should a deeper investigation start?')
        st.write('We examined a messy employee dataset, checked how cleaning decisions affect the findings, and built a transparent evidence scorecard.')
        a,b,c,d=st.columns(4)
        a.metric('Cleaned records',f'{len(base):,}')
        b.metric('Observed Left share',f'{base.Left.mean():.2%}')
        c.metric('Exact duplicates removed',f'{len(raw)-len(base):,}')
        d.metric('Comparisons checked','7')
        c1,c2=st.columns([1,1.2])
        with c1:
            counts=base.Attrition.value_counts().rename_axis('Outcome').reset_index(name='Records')
            chart(px.bar(counts,x='Outcome',y='Records',color='Outcome',color_discrete_map=COLOURS,title='Who is represented in this file?'))
        with c2:
            st.subheader('The strongest selected differences')
            st.write('Non-remote records have a **28.12 percentage-point** higher Left share than remote records. Poor/fair work-life balance has a **19.54-point** gap versus good/excellent balance.')
            st.info('These patterns motivate follow-up questions. They do not estimate what would happen if a company changed its policy.')
            st.write('Use **Data audit** to inspect reliability, **Explore groups** to choose cohorts, and **Evidence checks** to see uncertainty and sensitivity.')
        st.caption('47.48% is the fraction labelled Left in this dataset, not an annual attrition rate.')
    elif page=='Data audit':
        st.header('Before interpreting patterns, inspect the source')
        st.caption('This chapter always describes the full raw and baseline-cleaned datasets.')
        a,b,c=st.columns(3)
        a.metric('Raw records',f'{len(raw):,}');b.metric('Raw missing cells',f'{raw.isna().sum().sum():,}')
        c.metric('Baseline missing cells',f'{base.isna().sum().sum():,}')
        missing=read('data_quality_before.csv');missing=missing.loc[missing.missing_count.gt(0)]
        chart(px.bar(missing,x='column',y='missing_count',title='Missing values before deduplication',labels={'column':'Field','missing_count':'Missing cells'}))
        st.write('We remove only exact duplicates, repair two corrupted education labels, and median-impute two numeric fields while retaining missingness flags.')
        with st.expander('Quality concerns and decisions',expanded=True):
            st.write('151 incomes are outside IQR fences. The baseline retains them. Starting-age and tenure-definition concerns remain review flags; they are not proof of invalid records.')
            st.dataframe(read('outlier_audit.csv'),hide_index=True,width='stretch')
        st.subheader('Week 6: changing units is different from changing shape')
        st.image(str(ROOT/'Reports'/'Figures'/'06_income_transformations.png'))
        st.dataframe(read('feature_transformations.csv'),hide_index=True,width='stretch')
        st.caption('Transformations are used for descriptive PCA. All parameters were fitted on the full cohort; future prediction would require a fresh training-only fit.')
    elif page=='Explore groups':
        st.header('Explore an explicitly defined cohort')
        choice=st.sidebar.selectbox('Cleaning scenario',['Median / retain flags','Role-level median','Complete case','Exclude early-start flags','Income IQR capping'],key='scenario')
        roles=st.sidebar.multiselect('Job roles',sorted(base['Job Role'].unique()),default=sorted(base['Job Role'].unique()),key='roles')
        age=st.sidebar.slider('Age range',int(base.Age.min()),int(base.Age.max()),(int(base.Age.min()),int(base.Age.max())),key='age')
        cohort=filter_cohort(scenario_data(choice),roles,age)
        if cohort.empty:
            st.warning('No records match these filters. Select at least one role or widen the age range.');return
        a,b,c=st.columns(3)
        a.metric('Cohort records',f'{len(cohort):,}');b.metric('Observed Left share',f'{cohort.Left.mean():.2%}')
        c.metric('Share of baseline cohort',f'{len(cohort)/len(base):.1%}')
        st.caption(f'Scope: {choice}; selected roles and ages. Charts use all cohort rows unless a sample is stated.')
        tab1,tab2,tab3=st.tabs(['Group differences','Distributions','Relationships'])
        with tab1:
            field=st.selectbox('Compare by',['Remote Work','Work-Life Balance','Overtime','Job Role','Job Satisfaction','Employee Recognition'],key='group')
            rates=rate_table(cohort,field)
            rates['plus']=rates.ci_high_pct-rates.left_share_pct;rates['minus']=rates.left_share_pct-rates.ci_low_pct
            chart(px.bar(rates,x=field,y='left_share_pct',error_y='plus',error_y_minus='minus',hover_data=['n','left'],
                title='Observed Left share with 95% Wilson intervals',labels={'left_share_pct':'Left share (%)'}))
            st.caption('Hover for group sizes. These are unadjusted descriptive estimates; this cohort chart does not inherit the full-cohort evidence status.')
            st.download_button('Download cohort group table',rates.drop(columns=['plus','minus']).to_csv(index=False),'cohort_groups.csv','text/csv')
        with tab2:
            variable=st.selectbox('Numeric feature',NUMERIC,index=2,key='numeric')
            chart(px.histogram(cohort,x=variable,color='Attrition',nbins=45,barmode='overlay',opacity=.6,color_discrete_map=COLOURS,title='Distribution by outcome'))
            kind=st.radio('Distribution detail',['Box','Violin'],horizontal=True,key='distribution_kind')
            constructor=px.box if kind=='Box' else px.violin
            kwargs={'points':False} if kind=='Box' else {'points':False,'box':True}
            chart(constructor(cohort,x='Attrition',y=variable,color='Attrition',color_discrete_map=COLOURS,title=f'{kind} plot · {variable}',**kwargs))
        with tab3:
            sample=cohort.sample(min(3000,len(cohort)),random_state=42)
            chart(px.scatter(sample,x='Age',y='Years at Company',color='Attrition',opacity=.35,color_discrete_map=COLOURS,
                title=f'Age and tenure · fixed sample of {len(sample):,} records'))
            numeric=[c for c in NUMERIC if c!='Company Tenure (In Months)']
            chart(px.imshow(cohort[numeric].corr(method='spearman'),zmin=-1,zmax=1,color_continuous_scale='RdBu_r',text_auto='.2f',title='Spearman correlation · selected cohort'))
            st.caption('The ambiguous tenure-in-months field is excluded from this correlation view. Scatter points may overlap; no clusters are inferred.')
    elif page=='Evidence checks':
        st.header('Which claims survive the stated checks?')
        st.caption('All results in this chapter use the full cohort. Explore-group filters do not apply.')
        score=read('evidence_scorecard.csv')
        score['plus']=score.ci_high_pp-score.difference_pp;score['minus']=score.difference_pp-score.ci_low_pp
        chart(px.scatter(score,x='difference_pp',y='contrast',color='status',error_x='plus',error_x_minus='minus',
            hover_data=['exposed_n','reference_n','reason'],color_discrete_map={'Robust descriptive signal':'#147D92','Needs caution':'#E57B55'},
            title='Observed Left-share differences and 95% intervals',labels={'difference_pp':'Difference (percentage points)','contrast':''}))
        with st.expander('How the evidence gate works'):
            st.write('Each comparison needs at least 200 records in both arms, a gap of at least 5 percentage points, a consistent direction and interval excluding zero in all five cleaning scenarios, no more than a 2-point cleaning swing, consistent roles, and role/level standardization with at least 90% coverage. This is an exploratory project heuristic.')
        contrast=st.selectbox('Inspect a comparison',list(CONTRASTS),key='contrast')
        row=score.loc[score.contrast.eq(contrast)].iloc[0]
        st.write(f"**{row['status']}** — {row['reason']}")
        sens=read('cleaning_sensitivity.csv');sens=sens.loc[sens.contrast.eq(contrast)]
        chart(px.line(sens,x='scenario',y='difference_pp',markers=True,title='Sensitivity to cleaning choices',labels={'difference_pp':'Difference (pp)','scenario':'Cleaning scenario'}))
        within=read('within_role_comparisons.csv');within=within.loc[within.contrast.eq(contrast)]
        chart(px.bar(within,x='job_role',y='difference_pp',hover_data=['exposed_n','reference_n'],title='Does the direction persist within job roles?',labels={'difference_pp':'Difference (pp)','job_role':'Job role'}))
        st.caption('Income capping cannot directly change these categorical or distance contrasts. Its stable values are expected, not independent confirmation. Intervals are exploratory and not adjusted for multiple testing.')
        st.download_button('Download full evidence scorecard',score.drop(columns=['plus','minus']).to_csv(index=False),'evidence_scorecard.csv','text/csv')
    elif page=='PCA map':
        st.header('Compress the feature space without using the outcome')
        manifest=json.loads((ROOT/'Reports'/'advanced_manifest.json').read_text())
        a,b,c=st.columns(3)
        a.metric('Encoded features',manifest['selected_features']);b.metric('Components for 90%',manifest['components_retained'])
        c.metric('Variance retained',f"{manifest['retained_variance']:.2%}")
        variance=read('pca_variance.csv')
        fig=px.line(variance,x='component',y='cumulative_variance_ratio',markers=True,title='Cumulative explained variance')
        fig.add_hline(y=.90,line_dash='dash');chart(fig)
        roles=st.sidebar.multiselect('Job roles',sorted(base['Job Role'].unique()),default=sorted(base['Job Role'].unique()),key='pca_roles')
        age=st.sidebar.slider('Age range',int(base.Age.min()),int(base.Age.max()),(int(base.Age.min()),int(base.Age.max())),key='pca_age')
        scope=filter_cohort(base,roles,age)
        if scope.empty:st.warning('No records match the PCA display filters.');return
        coords=read('pca_coordinates.csv').merge(scope[['Employee ID','Job Role']],on='Employee ID',validate='one_to_one')
        sample=coords.sample(min(4000,len(coords)),random_state=42)
        mode=st.radio('Projection',['2D','3D'],horizontal=True,key='pca_mode')
        if mode=='2D':fig=px.scatter(sample,x='PC1',y='PC2',color='Attrition',opacity=.35,color_discrete_map=COLOURS)
        else:fig=px.scatter_3d(sample,x='PC1',y='PC2',z='PC3',color='Attrition',opacity=.4,color_discrete_map=COLOURS)
        fig.update_layout(title=f'PCA display · {len(sample):,} of {len(coords):,} filtered records');chart(fig)
        st.info(f"PC1+PC2 show only {manifest['first_two_variance']:.1%} of matrix variance. Colours are added after fitting. Overlap or visual separation is not measured prediction performance.")
        loads=read('pca_loadings.csv');top=loads.loc[loads.PC1.abs().nlargest(8).index].sort_values('PC1')
        chart(px.bar(top,x='PC1',y='feature',orientation='h',title='Largest PC1 coefficients'))
        st.caption(f"The PCA fit always uses the full baseline cohort. Display filters do not refit it. If all dummy columns are also standardized, the 90% target needs {manifest['all_columns_standardized_components_90']} components; geometry depends on weighting.")
    else:
        st.header('Turn observations into questions worth testing')
        st.subheader('1 · Verify the evidence source')
        st.write('Confirm sampling, dates, distance units, income units and the two tenure definitions with the dataset owner before applying the findings elsewhere.')
        st.subheader('2 · Investigate working conditions')
        st.write('Review how remote access and work-life balance vary by role, workload and team. Use voluntary qualitative feedback to understand the observed gaps.')
        st.subheader('3 · Evaluate a pilot prospectively')
        st.write('If an organization chooses a policy pilot, define outcomes and a comparable baseline in advance. Measure the pilot itself; do not use this dataset gap as a promised retention improvement.')
        st.subheader('4 · Withhold weak claims')
        st.write('Low recognition crosses zero in the difference interval. No promotions falls below the stated practical threshold. Keep these findings as open questions.')
        st.success('Deliverable: a reproducible visual evidence workflow with explicit uncertainty, documented transformations, PCA and interactive exploration.')
        st.markdown('[Dataset source](https://www.kaggle.com/datasets/nikhilbhosle/employee-attrition-uncleaned-dataset) · [Project repository](https://github.com/sauravsanthosh-prog/24ADI204_DSV_Team3/tree/main/DSV_PROJECT)')

if __name__=='__main__':main()
