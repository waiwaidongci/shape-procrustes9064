"""Alternating constrained GPA with unit consensus and fixed reference gauge."""
import numpy as np
from src.services.geometry import preshape,proper_rotation

def align_shapes(shapes,reference,tolerance=1e-12,max_iterations=100):
    if isinstance(max_iterations,bool) or not isinstance(max_iterations,int) or not 1<=max_iterations<=100:raise ValueError('GPA最多100步')
    if not 2<=len(shapes)<=120:raise ValueError('每集合须为2–120份形状')
    if not np.isfinite(tolerance) or not 1e-14<=tolerance<=1e-6:raise ValueError('收敛容差超出允许范围')
    ref,ref_info=preshape(reference);units=[];normalization=[]
    for points in shapes:
        x,info=preshape(points)
        if x.shape!=ref.shape:raise ValueError('同源角点数量与模板不一致')
        units.append(x);normalization.append(info)
    units=np.asarray(units);mean=ref.copy();rotations=np.asarray([proper_rotation(x,mean) for x in units]);aligned=np.asarray([x@r for x,r in zip(units,rotations)])
    objective=float(np.sum((aligned-mean)**2));history=[{'iteration':0,'objective':objective,'mean_delta':None}];termination={};effective=max(tolerance,np.finfo(float).eps*max(ref.shape)*16)
    for iteration in range(1,max_iterations+1):
        candidate_rot=np.asarray([proper_rotation(x,mean) for x in units]);candidate=np.asarray([x@r for x,r in zip(units,candidate_rot)]);arithmetic=candidate.mean(axis=0);norm=float(np.linalg.norm(arithmetic))
        if norm<=np.finfo(float).eps*max(ref.shape):raise ValueError('GPA共识在机器精度内为零，无法固定方向')
        new_mean=arithmetic/norm;gauge=proper_rotation(new_mean,ref);new_mean=new_mean@gauge;candidate=candidate@gauge;candidate_rot=candidate_rot@gauge
        new_obj=float(np.sum((candidate-new_mean)**2));delta=float(np.linalg.norm(new_mean-mean));roundoff=np.finfo(float).eps*64*len(units)
        if new_obj>objective+roundoff:raise ValueError(f'GPA目标增加超过机器误差界：{new_obj-objective:.6g}')
        roundoff_increase=bool(new_obj>objective)
        mean=new_mean;aligned=candidate;rotations=candidate_rot;objective=new_obj;history.append({'iteration':iteration,'objective':objective,'mean_delta':delta,'roundoff_increase':roundoff_increase,'roundoff_bound':roundoff})
        if delta<=effective:
            termination={'reason':'mean converged','checked_iteration':iteration};break
    else:raise ValueError('GPA超过100步仍未收敛，不能发布未收敛模态')
    return {'aligned':aligned,'gpa_mean':mean,'rotations':rotations,'preshapes':units,'normalization':normalization,'reference_normalized':ref,'reference_normalization':ref_info,'history':history,'iterations':len(history)-1,'converged':True,'effective_tolerance':effective,'termination':termination,'determinants':np.linalg.det(rotations).tolist()}
