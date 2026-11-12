"""Row-point shapes, centroid-size scaling, SO(2) rotations only."""
import numpy as np

def preshape(points):
    x=np.asarray(points,dtype=float)
    if x.ndim!=2 or x.shape[1]!=2 or not 3<=x.shape[0]<=64 or not np.isfinite(x).all():raise ValueError('轮廓须为有限二维同源点矩阵')
    centroid=x.mean(axis=0);centered=x-centroid;peak=float(np.max(np.abs(centered)))
    if not np.isfinite(centered).all() or peak==0:raise ValueError('退化轮廓：centroid-size为0或不可表示')
    scaled=centered/peak;length=float(np.linalg.norm(scaled));unit=scaled/length;size=peak*length
    if not np.isfinite(size):raise ValueError('轮廓尺度超出双精度范围')
    singular=np.linalg.svd(unit,compute_uv=False);rank_tolerance=np.finfo(float).eps*max(unit.shape)*singular[0]
    if singular[-1]<=rank_tolerance:raise ValueError('退化轮廓：同源点共线或二维秩不可解析')
    return unit,{'centroid':centroid.tolist(),'centroid_size':size,'rank_tolerance':float(rank_tolerance)}

def proper_rotation(x,y):
    if x.shape!=y.shape:raise ValueError('同源点数量不一致')
    u,_,vt=np.linalg.svd(x.T@y);d=np.eye(2);d[-1,-1]=1. if np.linalg.det(u@vt)>=0 else -1.
    return u@d@vt
