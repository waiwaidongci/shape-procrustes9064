"""Extrinsic PCA is centered on aligned arithmetic mean, never unit GPA mean."""
import hashlib,json
import numpy as np
from src.services.gpa import align_shapes

def shape_pca(aligned,retained=3):
    if isinstance(retained,bool) or not isinstance(retained,int) or not 1<=retained<=5:raise ValueError('保留模态须为1–5')
    x=np.asarray(aligned,dtype=float);flat=x.reshape(len(x),-1);mean=flat.mean(axis=0);centered=flat-mean;u,s,vt=np.linalg.svd(centered,full_matrices=False)
    for j in range(len(vt)):
        if vt[j,np.argmax(np.abs(vt[j]))]<0:vt[j]*=-1
    # Resolve variation relative to unit-aligned data and IEEE precision, not a
    # large absolute variance cutoff. Same-shape floating noise must not invent axes.
    noise_floor=float(np.finfo(float).eps*max(flat.shape)*np.linalg.norm(flat));active=int(np.sum(s>noise_floor));k=min(retained,active);total=float(np.sum(s*s));scores=centered@vt.T;reconstruction=mean+scores[:,:k]@vt[:k];residual=np.linalg.norm(flat-reconstruction,axis=1)
    ratios=(s*s/total).tolist() if active else [];eigenvalues=s*s/(len(x)-1);modes=[]
    for j in range(k):
        sd=float(np.sqrt(eigenvalues[j]));modes.append({'index':j+1,'singular_value':float(s[j]),'eigenvalue':float(eigenvalues[j]),'explained_ratio':ratios[j],'sd':sd,'loading':vt[j].reshape(x.shape[1:]).tolist(),'minus_2sd':(mean-2*sd*vt[j]).reshape(x.shape[1:]).tolist(),'plus_2sd':(mean+2*sd*vt[j]).reshape(x.shape[1:]).tolist()})
    return {'arithmetic_mean':mean.reshape(x.shape[1:]).tolist(),'mean_norm':float(np.linalg.norm(mean)),'singular_values':s.tolist(),'eigenvalues':eigenvalues.tolist(),'explained_ratio':ratios,'active_rank':active,'retained_explained_ratio':float(sum(ratios[:k])) if active else None,'retained':k,'requested':retained,'noise_floor':noise_floor,'has_variation':active>0,'right_singular_vectors':vt.tolist(),'all_scores':scores.tolist(),'scores':scores[:,:k].tolist(),'reconstruction':reconstruction.reshape(x.shape).tolist(),'residual':residual.tolist(),'modes':modes,'total_centered_ss':total}

def analyze_alignment(snapshot,retained,tolerance):
    specimens=sorted(snapshot['specimens'],key=lambda s:s['code']);template=snapshot['template']
    if len({s['id'] for s in specimens})!=len(specimens) or len({s['code'] for s in specimens})!=len(specimens):raise ValueError('裁片标识重复')
    if len(template['labels'])!=8 or len(set(template['labels']))!=8:raise ValueError('模板须有8个不同同源标签')
    if np.asarray(template['points']).shape!=(8,2) or any(np.asarray(s['points']).shape!=(8,2) for s in specimens):raise ValueError('每份裁片必须按同源顺序提供8×2点')
    gpa=align_shapes([s['points'] for s in specimens],template['points'],tolerance);pca=shape_pca(gpa['aligned'],retained);rows=[]
    for i,s in enumerate(specimens):rows.append({**s,**gpa['normalization'][i],'preshape':gpa['preshapes'][i].tolist(),'rotation':gpa['rotations'][i].tolist(),'rotation_determinant':gpa['determinants'][i],'aligned':gpa['aligned'][i].tolist(),'gpa_distance':float(np.linalg.norm(gpa['aligned'][i]-gpa['gpa_mean'])),'scores':pca['scores'][i],'reconstruction':pca['reconstruction'][i],'residual':pca['residual'][i]})
    normalized_snapshot={**snapshot,'specimens':specimens};canonical={'algorithm':'so2-unit-gpa-arithmetic-pca-v1','snapshot':normalized_snapshot,'retained':retained,'tolerance':tolerance};fingerprint=hashlib.sha256(json.dumps(canonical,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
    return {'specimens':rows,'labels':template['labels'],'gpa_mean':gpa['gpa_mean'].tolist(),'gpa_mean_norm':float(np.linalg.norm(gpa['gpa_mean'])),'reference_normalized':gpa['reference_normalized'].tolist(),'history':gpa['history'],'iterations':gpa['iterations'],'converged':gpa['converged'],'effective_tolerance':gpa['effective_tolerance'],'termination':gpa['termination'],'determinant_min':min(gpa['determinants']),'pca':pca,'mean_difference':float(np.linalg.norm(gpa['gpa_mean']-np.asarray(pca['arithmetic_mean']))),'fingerprint':fingerprint,'snapshot':normalized_snapshot,'scope':'SO(2) rotations only; fixed homologous labels; extrinsic linear modes are not manufacturing instructions'}
