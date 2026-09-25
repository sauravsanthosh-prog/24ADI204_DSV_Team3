"""Weeks 6-7: label-free descriptive transformations and PCA.

Fit on the full cleaned cohort for exploration, not predictive evaluation.
No employee identifier, attrition label, or derived outcome enters the matrix.
"""
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder, PowerTransformer, StandardScaler
from attrition_lab import ROOT, NUMERIC, load_raw, clean_data

NUM_FEATURES = [c for c in NUMERIC if c != 'Company Tenure (In Months)']
CAT_FEATURES = ['Gender', 'Job Role', 'Work-Life Balance', 'Job Satisfaction',
    'Performance Rating', 'Overtime', 'Education Level', 'Marital Status', 'Job Level',
    'Company Size', 'Remote Work', 'Leadership Opportunities', 'Innovation Opportunities',
    'Company Reputation', 'Employee Recognition']
EXCLUDED = {'Employee ID': 'Identifier, no analytical distance meaning',
    'Attrition': 'Outcome excluded from unsupervised fit', 'Left': 'Derived outcome excluded',
    'Company Tenure (In Months)': 'Definition conflicts with Years at Company; unresolved',
    'Distance from Home Missing': 'Audit flag, kept outside primary PCA',
    'Company Tenure (In Months) Missing': 'Audit flag, kept outside primary PCA',
    'Early Start Flag': 'Audit assumption, kept outside primary PCA',
    'Tenure Definition Review': 'Audit assumption, kept outside primary PCA',
    'Income IQR Flag': 'Audit flag, kept outside primary PCA'}

def transform_features(clean):
    """Transform only markedly skewed numeric fields when Yeo-Johnson reduces skew.

    Standardize numeric features. One-hot encode all categorical fields without
    assuming equal ordinal distances, dropping one reference per field to avoid
    exact dummy redundancy. Keep dummies at 0/1; mixed-type PCA is scale-sensitive.
    """
    nums = clean[NUM_FEATURES].astype(float).copy()
    shaped = nums.copy()
    decisions = []
    for c in nums:
        before = float(nums[c].skew())
        applied = 'Identity'; lam = None; candidate = before
        if abs(before) > 1 and nums[c].nunique() > 2:
            pt = PowerTransformer(method='yeo-johnson', standardize=False)
            values = pt.fit_transform(nums[[c]]).ravel()
            candidate = float(pd.Series(values).skew())
            if abs(candidate) < abs(before):
                shaped[c] = values
                applied = 'Yeo-Johnson'; lam = float(pt.lambdas_[0])
        decisions.append({'feature': c, 'raw_skew': before, 'candidate_yj_skew': candidate,
            'applied': applied, 'lambda': lam, 'selected_skew': float(shaped[c].skew())})
    scaler = StandardScaler()
    standardized = pd.DataFrame(scaler.fit_transform(shaped),columns=NUM_FEATURES,index=clean.index)
    minmax = pd.DataFrame(MinMaxScaler().fit_transform(nums),columns=NUM_FEATURES,index=clean.index)
    enc = OneHotEncoder(drop='first',handle_unknown='error',sparse_output=False,dtype=np.float64)
    dummies = enc.fit_transform(clean[CAT_FEATURES].astype(str))
    names = list(enc.get_feature_names_out(CAT_FEATURES))
    matrix = pd.concat([standardized,pd.DataFrame(dummies,columns=names,index=clean.index)],axis=1)
    if not np.isfinite(matrix.to_numpy()).all():
        raise ValueError('Transformed matrix contains nonfinite values')
    encoding = pd.DataFrame([{'feature': c,'categories': ' | '.join(map(str,cats)),
        'reference_category': str(cats[0]),'output_columns':len(cats)-1}
        for c,cats in zip(CAT_FEATURES,enc.categories_)])
    scaling = pd.DataFrame({'feature':NUM_FEATURES,'center_after_shape_transform':scaler.mean_,
        'scale_after_shape_transform':scaler.scale_, 'standard_mean':standardized.mean().values,
        'standard_std_ddof0':standardized.std(ddof=0).values,
        'minmax_min':minmax.min().values,'minmax_max':minmax.max().values})
    return {'matrix':matrix,'numeric_raw':nums,'numeric_shaped':shaped,
        'standardized':standardized,'minmax':minmax,'transformations':pd.DataFrame(decisions),
        'encoding':encoding,'scaling':scaling}

def select_correlated(matrix, threshold=.90):
    """Drop constants and later columns correlated with an already kept column.

    This is a pairwise screening rule, not proof that all multicollinearity is gone.
    Fixed source-column order makes ties reproducible; no outcome guides selection.
    """
    corr = matrix.corr()
    kept, decisions = [], []
    for c in matrix:
        if matrix[c].nunique() <= 1:
            decisions.append({'feature':c,'action':'drop','reason':'constant','paired_with':'','abs_r':np.nan})
            continue
        peers = [(k,abs(float(corr.loc[c,k]))) for k in kept if abs(corr.loc[c,k]) > threshold]
        if peers:
            k,r=max(peers,key=lambda x:x[1])
            decisions.append({'feature':c,'action':'drop','reason':f'|Pearson r| > {threshold}', 'paired_with':k,'abs_r':r})
        else:
            kept.append(c)
            decisions.append({'feature':c,'action':'keep','reason':'passes pairwise screen','paired_with':'','abs_r':np.nan})
    return matrix[kept],pd.DataFrame(decisions),corr

def fit_pca(matrix, variance_target=.90):
    if not 0 < variance_target < 1:
        raise ValueError('Variance target must lie strictly between 0 and 1')
    model=PCA(svd_solver='full')
    scores=model.fit_transform(matrix)
    ratio=model.explained_variance_ratio_
    n=int(np.searchsorted(np.cumsum(ratio),variance_target)+1)
    variance=pd.DataFrame({'component':np.arange(1,len(ratio)+1),
        'explained_variance_ratio':ratio,'cumulative_variance_ratio':np.cumsum(ratio)})
    reconstructed=scores[:,:n]@model.components_[:n]+model.mean_
    residual=float(np.square(matrix.to_numpy()-reconstructed).sum())
    total=float(np.square(matrix.to_numpy()-matrix.mean().to_numpy()).sum())
    # A second numerical check, independent of the component-count selection.
    retained=1-residual/total
    return {'model':model,'scores':scores,'n_components':n,'variance':variance,
        'retained_variance':retained,
        'loadings':pd.DataFrame(model.components_.T,index=matrix.columns,
            columns=[f'PC{i+1}' for i in range(len(ratio))])}

def save_figures(features, selected, result, clean):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import seaborn as sns
    dest=ROOT/'Reports'/'Figures'; dest.mkdir(exist_ok=True,parents=True)
    sns.set_theme(style='whitegrid',palette=['#176B87','#DA7652'])
    def save(name):
        plt.tight_layout(); plt.savefig(dest/f'{name}.png',dpi=145,bbox_inches='tight');plt.close()
    fig,axes=plt.subplots(1,3,figsize=(12,3.7))
    c='Monthly Income'
    for ax,values,title in zip(axes,[features['numeric_raw'][c],features['minmax'][c],features['standardized'][c]],
        ['Original income','MinMax only (shape unchanged)','Selected transform + standardize']):
        ax.hist(values,bins=45,color='#176B87');ax.set_title(title);ax.set_ylabel('Records')
        ax.set_xlabel(f'Skew = {values.skew():.3f}')
    save('06_income_transformations')
    fig,axes=plt.subplots(1,2,figsize=(12,4))
    features['numeric_raw'].boxplot(ax=axes[0],rot=30);axes[0].set_title('Original numeric units')
    features['standardized'].boxplot(ax=axes[1],rot=30);axes[1].set_title('Shape transform + StandardScaler')
    save('06_scaling_comparison')
    plt.figure(figsize=(8,6));sns.heatmap(features['standardized'].corr(),vmin=-1,vmax=1,cmap='vlag',annot=True,fmt='.2f')
    plt.title('Numeric Pearson correlations after transformation');save('07_numeric_correlation')
    v=result['variance']; n=result['n_components']
    fig,axes=plt.subplots(1,2,figsize=(12,4))
    axes[0].bar(v.component,v.explained_variance_ratio,color='#176B87');axes[0].set(title='PCA explained variance',xlabel='Component',ylabel='Variance ratio')
    axes[1].plot(v.component,v.cumulative_variance_ratio,marker='.',color='#176B87')
    axes[1].axhline(.90,color='#DA7652',linestyle='--',label='90% target')
    axes[1].axvline(n,color='#DA7652',linestyle=':',label=f'{n} components')
    axes[1].set(xlabel='Components retained',ylabel='Cumulative variance',ylim=(0,1.03));axes[1].legend()
    save('07_explained_variance')
    sample=clean.sample(min(4000,len(clean)),random_state=42).index
    coords=result['scores']
    plt.figure(figsize=(9,5.5))
    for label,color in [('Stayed','#176B87'),('Left','#DA7652')]:
        ix=sample[clean.loc[sample,'Attrition'].eq(label)]
        plt.scatter(coords[ix,0],coords[ix,1],s=7,alpha=.3,c=color,label=label)
    plt.xlabel(f'PC1 ({v.explained_variance_ratio.iloc[0]:.1%})');plt.ylabel(f'PC2 ({v.explained_variance_ratio.iloc[1]:.1%})')
    plt.title('PCA projection | fixed sample; outcome used only for colour');plt.legend();save('07_pca_scatter')
    loads=result['loadings']; top=loads.PC1.abs().nlargest(8).index
    plt.figure(figsize=(9,4.7));loads.loc[top,'PC1'].sort_values().plot.barh(color='#176B87')
    plt.xlabel('Component coefficient (sign is arbitrary)');plt.title('Largest absolute PC1 coefficients');save('07_pca_loadings')

def build_advanced():
    raw=load_raw(); clean=clean_data(raw)
    features=transform_features(clean)
    selected,decisions,corr=select_correlated(features['matrix'])
    result=fit_pca(selected)
    reports=ROOT/'Reports'; reports.mkdir(exist_ok=True)
    dest=ROOT/'Dataset'/'Processed';dest.mkdir(parents=True,exist_ok=True)
    for key in ['transformations','encoding','scaling']:
        features[key].to_csv(reports/f'feature_{key}.csv',index=False)
    decisions.to_csv(reports/'feature_selection.csv',index=False)
    corr.to_csv(reports/'encoded_correlation.csv')
    pd.DataFrame(EXCLUDED.items(),columns=['feature','reason']).to_csv(reports/'feature_exclusions.csv',index=False)
    result['variance'].to_csv(reports/'pca_variance.csv',index=False)
    result['loadings'].rename_axis('feature').to_csv(reports/'pca_loadings.csv')
    np.savez_compressed(dest/'features_and_components.npz',
        X=selected.to_numpy(dtype=np.float32),feature_names=np.array(selected.columns,dtype=str),
        employee_ids=clean['Employee ID'].to_numpy(),
        scores=result['scores'][:,:result['n_components']].astype(np.float32))
    coords=clean[['Employee ID','Attrition']].copy()
    coords[['PC1','PC2','PC3']]=result['scores'][:,:3]
    coords.to_csv(reports/'pca_coordinates.csv',index=False)
    # Sensitivity to weighting: standardize all one-hot columns as a comparator.
    alternative=fit_pca(pd.DataFrame(StandardScaler().fit_transform(selected),columns=selected.columns))
    summary={'rows':len(clean),'input_original_features':len(NUM_FEATURES)+len(CAT_FEATURES),
        'encoded_features':features['matrix'].shape[1],'selected_features':selected.shape[1],
        'correlation_threshold':.90,'dropped_correlated_or_constant':int(decisions.action.eq('drop').sum()),
        'variance_target':.90,'components_retained':result['n_components'],
        'retained_variance':result['retained_variance'],
        'first_two_variance':float(result['variance'].explained_variance_ratio.iloc[:2].sum()),
        'all_columns_standardized_components_90':alternative['n_components'],
        'all_columns_standardized_first_two_variance':float(alternative['variance'].explained_variance_ratio.iloc[:2].sum()),
        'raw_sha256':hashlib.sha256((ROOT/'Dataset'/'Raw'/'Emp_attrition_csv.csv').read_bytes()).hexdigest(),
        'fit_scope':'Full cleaned cohort; descriptive PCA only; no prediction evaluation',
        'weighting':'Numeric z-scores + reference-dropped unscaled one-hot columns',
        'target_in_features':False,'identifier_in_features':False}
    (reports/'advanced_manifest.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    save_figures(features,selected,result,clean)
    print(json.dumps(summary,indent=2))
    return summary

if __name__=='__main__': build_advanced()
