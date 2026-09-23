"""Reproducible Week 1-4 data audit, cleaning and descriptive evidence checks.

No prediction model, causal effect, or individual employee score is produced.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'Dataset' / 'Raw' / 'Emp_attrition_csv.csv'
NUMERIC = ['Age', 'Years at Company', 'Monthly Income', 'Number of Promotions',
           'Distance from Home', 'Number of Dependents', 'Company Tenure (In Months)']
MISSING = ['Distance from Home', 'Company Tenure (In Months)']
ORDERS = {
    'Work-Life Balance': ['Poor', 'Fair', 'Good', 'Excellent'],
    'Job Satisfaction': ['Low', 'Medium', 'High', 'Very High'],
    'Performance Rating': ['Low', 'Below Average', 'Average', 'High'],
    'Job Level': ['Entry', 'Mid', 'Senior'],
    'Company Size': ['Small', 'Medium', 'Large'],
    'Employee Recognition': ['Low', 'Medium', 'High', 'Very High'],
    'Company Reputation': ['Poor', 'Fair', 'Good', 'Excellent'],
}
CONTRASTS = {
    'Overtime': ('Overtime', ['Yes'], ['No']),
    'Limited remote access': ('Remote Work', ['No'], ['Yes']),
    'Poor or fair balance': ('Work-Life Balance', ['Poor', 'Fair'], ['Good', 'Excellent']),
    'Low satisfaction': ('Job Satisfaction', ['Low'], ['Medium', 'High', 'Very High']),
    'Low recognition': ('Employee Recognition', ['Low'], ['Medium', 'High', 'Very High']),
    'No promotions': ('Number of Promotions', [0], [1, 2, 3, 4]),
    'Long commute (50+ recorded units)': ('Distance from Home', None, None),
}

def load_raw():
    data = pd.read_csv(RAW)
    required = set(NUMERIC + ['Employee ID', 'Attrition', 'Job Role', 'Job Level'])
    if not required.issubset(data.columns):
        raise ValueError(f'Missing required fields: {required - set(data.columns)}')
    if data['Attrition'].isna().any() or not set(data['Attrition'].unique()) <= {'Stayed', 'Left'}:
        raise ValueError('Target labels must be known Stayed/Left values; do not impute labels.')
    return data

def quality_report(data):
    return pd.DataFrame({
        'dtype': data.dtypes.astype(str), 'missing_count': data.isna().sum(),
        'missing_pct': data.isna().mean().mul(100),
        'unique_non_null': data.nunique(),
        'constant': data.nunique().le(1),
    }).rename_axis('column').reset_index()

def outlier_report(data):
    rows = []
    for col in NUMERIC:
        x = data[col].dropna()
        q1, q3 = x.quantile([.25, .75]); iqr = q3 - q1
        lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        std = x.std(ddof=0)
        rows.append({'column': col, 'iqr_low': lo, 'iqr_high': hi,
                     'iqr_flagged': int(((x < lo) | (x > hi)).sum()),
                     'z_gt_3_flagged': int(((x-x.mean()).abs() / std > 3).sum()) if std else 0,
                     'policy': 'Flag and retain; no automatic deletion'})
    return pd.DataFrame(rows)

def clean_data(raw, strategy='median'):
    """Remove only exact duplicates; repair known mojibake; preserve suspicious rows.

    Group medians use role + level and fall back to the overall median. Neither
    imputation strategy uses Attrition. These are descriptive EDA transformations;
    a later predictive pipeline must fit transformations on training data only.
    """
    if strategy not in {'median', 'group_median', 'complete_case'}:
        raise ValueError(f'Unknown strategy: {strategy}')
    d = raw.drop_duplicates().copy()
    if d['Employee ID'].duplicated().any():
        raise ValueError('Conflicting employee IDs need review; cannot deduplicate by ID silently.')
    text_cols = d.select_dtypes(include=['object', 'str', 'string']).columns
    for c in text_cols:
        d[c] = d[c].str.strip()
    # Explicitly repair the two observed labels instead of guessing every string's encoding.
    d['Education Level'] = d['Education Level'].replace({
        'Bachelor\u00e2\u20ac\u2122s Degree': "Bachelor's Degree",
        'Master\u00e2\u20ac\u2122s Degree': "Master's Degree",
    })
    for col in MISSING:
        d[col + ' Missing'] = d[col].isna()
    d['Early Start Flag'] = d['Age'] - d['Years at Company'] < 14
    # Both names appear to describe tenure, but their semantics are unverified.
    # This comparison is a review flag, not proof either field is incorrect.
    d['Tenure Definition Review'] = (d['Years at Company'] * 12 - d['Company Tenure (In Months)']).abs() > 12
    x = d['Monthly Income']; q1, q3 = x.quantile([.25, .75])
    d['Income IQR Flag'] = (x < q1 - 1.5*(q3-q1)) | (x > q3 + 1.5*(q3-q1))
    if strategy == 'complete_case':
        d = d.dropna(subset=MISSING).copy()
    else:
        for col in MISSING:
            if strategy == 'group_median':
                medians = d.groupby(['Job Role', 'Job Level'], observed=True)[col].transform('median')
                d[col] = d[col].fillna(medians)
            d[col] = d[col].fillna(d[col].median())
    d['Left'] = d['Attrition'].eq('Left').astype(int)
    return d.reset_index(drop=True)

def scenarios(raw):
    base = clean_data(raw)
    capped = base.copy()
    q1, q3 = base['Monthly Income'].quantile([.25, .75])
    capped['Monthly Income'] = capped['Monthly Income'].clip(q1-1.5*(q3-q1), q3+1.5*(q3-q1))
    return {
        'Median / retain flags': base,
        'Role-level median': clean_data(raw, 'group_median'),
        'Complete case': clean_data(raw, 'complete_case'),
        'Exclude early-start flags': base.loc[~base['Early Start Flag']].copy(),
        'Income IQR capping': capped,
    }

def wilson(k, n, z=1.959963984540054):
    """Two-sided 95% Wilson interval for an independent binomial proportion."""
    if n == 0:
        return np.nan, np.nan
    p = k/n; den = 1+z*z/n
    center = (p + z*z/(2*n))/den
    half = z*np.sqrt(p*(1-p)/n + z*z/(4*n*n))/den
    return max(0., center-half), min(1., center+half)

def rate_table(data, columns):
    t = data.groupby(columns, observed=True, dropna=False)['Left'].agg(n='size', left='sum').reset_index()
    t['left_share_pct'] = 100*t['left']/t['n']
    ci = [wilson(k,n) for k,n in zip(t['left'],t['n'])]
    t['ci_low_pct'] = [100*v[0] for v in ci]
    t['ci_high_pct'] = [100*v[1] for v in ci]
    return t

def contrast_masks(data, name):
    col, exposed, reference = CONTRASTS[name]
    if exposed is None:
        return data[col].ge(50), data[col].lt(50)
    return data[col].isin(exposed), data[col].isin(reference)

def compare(data, name):
    """Unadjusted difference with Newcombe's Wilson-based 95% interval."""
    e, r = contrast_masks(data, name)
    a, b = data.loc[e, 'Left'], data.loc[r, 'Left']
    if not len(a) or not len(b):
        return {'exposed_n': len(a), 'reference_n': len(b), 'difference_pp': np.nan,
                'ci_low_pp': np.nan, 'ci_high_pp': np.nan}
    p, q = a.mean(), b.mean(); la, ua = wilson(a.sum(),len(a)); lb, ub = wilson(b.sum(),len(b))
    return {'exposed_n': len(a), 'reference_n': len(b),
            'difference_pp': 100*(p-q),
            'ci_low_pp': 100*((p-q)-np.sqrt((p-la)**2+(ub-q)**2)),
            'ci_high_pp': 100*((p-q)+np.sqrt((ua-p)**2+(q-lb)**2))}

def evidence_tables(raw, min_n=200, practical_pp=5., max_swing_pp=2.):
    """Transparent project screening thresholds, not a validated decision rule."""
    variants = scenarios(raw); base = next(iter(variants.values()))
    sensitivity = pd.DataFrame([
        {'contrast': name, 'scenario': label, **compare(data, name)}
        for name in CONTRASTS for label,data in variants.items()
    ])
    within = pd.DataFrame([
        {'contrast': name, 'job_role': role, **compare(group, name)}
        for name in CONTRASTS for role,group in base.groupby('Job Role', observed=True)
    ])
    # Direct standardization to the shared role x level distribution. This does
    # not control for unmeasured confounding and does not estimate interventions.
    adjusted = []
    for name in CONTRASTS:
        rows = []
        for (role,level),g in base.groupby(['Job Role','Job Level'], observed=True):
            e,r = contrast_masks(g,name)
            if e.sum() >= min_n and r.sum() >= min_n:
                rows.append((len(g), g.loc[e,'Left'].mean()-g.loc[r,'Left'].mean()))
        den = sum(n for n,_ in rows)
        adjusted.append({'contrast': name, 'standardized_difference_pp':
                         100*sum(n*delta for n,delta in rows)/den if den else np.nan,
                         'covered_population_pct': 100*den/len(base), 'eligible_strata': len(rows)})
    adjusted = pd.DataFrame(adjusted)
    summary = []
    for name in CONTRASTS:
        s = sensitivity[sensitivity.contrast.eq(name)]
        w = within[within.contrast.eq(name)]
        b = compare(base,name); sign = np.sign(b['difference_pp'])
        enough = bool((s[['exposed_n','reference_n']] >= min_n).all().all())
        same = bool((np.sign(s.difference_pp) == sign).all())
        clear = bool(((s.ci_low_pp > 0) | (s.ci_high_pp < 0)).all())
        role_stable = bool((np.sign(w.difference_pp) == sign).all() and
                           (w[['exposed_n','reference_n']] >= min_n).all().all())
        swing = s.difference_pp.max()-s.difference_pp.min()
        meaningful = bool(s.difference_pp.abs().min() >= practical_pp)
        adj = adjusted[adjusted.contrast.eq(name)].iloc[0]
        adjusted_ok = bool(np.sign(adj.standardized_difference_pp) == sign and
                           abs(adj.standardized_difference_pp) >= practical_pp and
                           adj.covered_population_pct >= 90)
        passed = enough and same and clear and role_stable and meaningful and swing <= max_swing_pp and adjusted_ok
        failures = []
        for condition,reason in [(enough,'small sample'),(same,'direction changes'),(clear,'interval crosses zero'),
                                  (role_stable,'role inconsistency'),(meaningful,'below practical threshold'),
                                  (swing<=max_swing_pp,'cleaning sensitive'),(adjusted_ok,'adjusted effect or coverage')]:
            if not condition: failures.append(reason)
        summary.append({'contrast': name, **b, 'cleaning_swing_pp': swing,
                        'all_roles_same_direction': role_stable,
                        'status': 'Robust descriptive signal' if passed else 'Needs caution',
                        'reason': '; '.join(failures) if failures else 'Passed stated exploratory checks'})
    return pd.DataFrame(summary).merge(adjusted,on='contrast'), sensitivity, within

def build_artifacts():
    raw = load_raw(); clean = clean_data(raw)
    reports = ROOT/'Reports'; reports.mkdir(parents=True, exist_ok=True)
    processed = ROOT/'Dataset'/'Cleaned'; processed.mkdir(parents=True, exist_ok=True)
    quality_report(raw).to_csv(reports/'data_quality_before.csv',index=False)
    quality_report(clean).to_csv(reports/'data_quality_after.csv',index=False)
    outlier_report(raw.drop_duplicates()).to_csv(reports/'outlier_audit.csv',index=False)
    clean.to_csv(processed/'employee_attrition_cleaned.csv',index=False)
    flags = ['Distance from Home Missing','Company Tenure (In Months) Missing',
             'Early Start Flag','Tenure Definition Review','Income IQR Flag']
    clean[['Employee ID']+flags].to_csv(reports/'row_quality_flags.csv',index=False)
    desc = clean[NUMERIC].describe().T
    desc['median'] = clean[NUMERIC].median(); desc['variance'] = clean[NUMERIC].var()
    desc['skewness'] = clean[NUMERIC].skew(); desc['excess_kurtosis'] = clean[NUMERIC].kurt()
    desc.to_csv(reports/'descriptive_statistics.csv')
    summary,sens,within = evidence_tables(raw)
    summary.to_csv(reports/'evidence_scorecard.csv',index=False)
    sens.to_csv(reports/'cleaning_sensitivity.csv',index=False)
    within.to_csv(reports/'within_role_comparisons.csv',index=False)
    pd.concat([rate_table(clean,c).rename(columns={c:'category'}).assign(feature=c)
               for c in raw.select_dtypes(include=['object','str','string']).columns if c!='Attrition']
             ).to_csv(reports/'categorical_left_shares.csv',index=False)
    variants = scenarios(raw)
    pd.DataFrame([{'scenario':name,'rows':len(d),'left_share_pct':100*d.Left.mean(),
                   'income_mean':d['Monthly Income'].mean(),'income_median':d['Monthly Income'].median(),
                   'commute_median':d['Distance from Home'].median()}
                  for name,d in variants.items()]).to_csv(reports/'scenario_summary.csv',index=False)
    manifest = {'dataset_source':'https://www.kaggle.com/datasets/nikhilbhosle/employee-attrition-uncleaned-dataset',
                'sha256':hashlib.sha256(RAW.read_bytes()).hexdigest(),
                'raw_rows':len(raw),'raw_columns':len(raw.columns),'exact_duplicates_removed':len(raw)-len(clean),
                'clean_rows':len(clean),'missing_cells_before':int(raw.isna().sum().sum()),
                'missing_cells_after':int(clean.isna().sum().sum()),
                'left_count':int(clean.Left.sum()),'left_share_pct':float(100*clean.Left.mean()),
                'flags':{c:int(clean[c].sum()) for c in flags},
                'scope':'Week 1-4 descriptive analysis only',
                'thresholds':{'min_group_n':200,'practical_difference_pp':5,'max_cleaning_swing_pp':2},
                'uncertainty':'Intervals assume independent rows; sampling and company clusters unknown.'}
    (reports/'run_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    return manifest

if __name__ == '__main__':
    print(json.dumps(build_artifacts(),indent=2))
