import csv,io
from sqlalchemy import select
from fastapi import HTTPException
from src.models import InspectionNote
from src.services.run_service import get_run
from src.constants.enums import NoteStatus

def list_notes(db):return db.scalars(select(InspectionNote).order_by(InspectionNote.id.desc())).all()
def create_note(db,data):
    r=get_run(db,data.run_id)
    if r.status!='completed':raise HTTPException(409,'须依据已完成对齐结果')
    if data.specimen_id not in {s['id'] for s in r.result['specimens']}:raise HTTPException(422,'裁片须来自本次冻结集合')
    if db.scalar(select(InspectionNote).where(InspectionNote.name==data.name)):raise HTTPException(409,'复验说明名称重复')
    n=InspectionNote(**data.model_dump());db.add(n);db.commit();return n

def review_note(db,id,data,user):
    n=db.get(InspectionNote,id)
    if not n:raise HTTPException(404,'复验说明不存在')
    if n.status!=NoteStatus.DRAFT:raise HTTPException(409,'不能覆盖已留档审阅')
    if data.status not in (NoteStatus.APPROVED,NoteStatus.REJECTED):raise HTTPException(422,'请选择同意或退回')
    n.status=data.status;n.reviewer_note=data.reviewer_note;n.reviewed_by=user.email;db.commit();return n

def export_note(db,id):
    n=db.get(InspectionNote,id)
    if not n:raise HTTPException(404,'复验说明不存在')
    if n.status!=NoteStatus.APPROVED:raise HTTPException(409,'批准后才可分发')
    r=get_run(db,n.run_id).result;out=io.StringIO();w=csv.writer(out)
    w.writerow(['note','specimen_id','reviewer','reviewer_note','protocol','fingerprint','scope']);w.writerow([n.name,n.specimen_id,n.reviewed_by,n.reviewer_note,n.protocol,r['fingerprint'],'禁反射；PCA用算术均值；线性模态不保证可制造'])
    w.writerow(['iterations','converged','objective_initial','objective_final','gpa_mean_norm','pca_mean_norm','active_rank','retained']);w.writerow([r['iterations'],r['converged'],r['history'][0]['objective'],r['history'][-1]['objective'],r['gpa_mean_norm'],r['pca']['mean_norm'],r['pca']['active_rank'],r['pca']['retained']])
    w.writerow(['specimen','centroid_x','centroid_y','centroid_size','rotation_det','gpa_distance','pca_residual'])
    for s in r['specimens']:w.writerow([s['code'],*s['centroid'],s['centroid_size'],s['rotation_determinant'],s['gpa_distance'],s['residual']])
    w.writerow(['specimen','label','raw_x','raw_y','aligned_x','aligned_y','reconstruction_x','reconstruction_y'])
    for s in r['specimens']:
        for i,label in enumerate(r['labels']):w.writerow([s['code'],label,*s['points'][i],*s['aligned'][i],*s['reconstruction'][i]])
    w.writerow(['label','gpa_unit_mean_x','gpa_unit_mean_y','pca_arithmetic_mean_x','pca_arithmetic_mean_y'])
    for i,label in enumerate(r['labels']):w.writerow([label,*r['gpa_mean'][i],*r['pca']['arithmetic_mean'][i]])
    w.writerow(['mode','label','singular_value','explained_ratio','minus2sd_x','minus2sd_y','plus2sd_x','plus2sd_y'])
    for m in r['pca']['modes']:
        for i,label in enumerate(r['labels']):w.writerow([m['index'],label,m['singular_value'],m['explained_ratio'],*m['minus_2sd'][i],*m['plus_2sd'][i]])
    return '\ufeff'+out.getvalue()
