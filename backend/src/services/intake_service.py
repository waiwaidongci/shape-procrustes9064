import hashlib,json,math,re,uuid
from datetime import datetime
from sqlalchemy import select,func
from fastapi import HTTPException
from src.models import ShapeSpecimen,IntakeBatch
from src.services.collection_service import get_collection
from src.services.template_service import get_template
from src.services.specimen_service import list_specimens
from src.constants.enums import IntakeStatus

SPECIMEN_LIMIT=120
CODE=re.compile(r'^[A-Za-z0-9_-]+$')

def state_fingerprint(db,collection):
    t=get_template(db,collection.template_id)
    payload={'collection':{k:getattr(collection,k) for k in ('id','code','name','template_id','protocol','source_file')},'template':{k:getattr(t,k) for k in ('id','code','name','labels','points','convention')},'specimens':[{k:getattr(s,k) for k in ('id','code','name','points','source_note')} for s in list_specimens(db,collection.id)]}
    return hashlib.sha256(json.dumps(payload,ensure_ascii=False,sort_keys=True).encode()).hexdigest()

def _number(v):return isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v) and abs(v)<=1e6

def validate_row(index,row,template,existing,seen):
    reasons=[];code=row.get('code');name=row.get('name');source_note=row.get('source_note','');labels=row.get('labels');points=row.get('points')
    if not isinstance(code,str) or not(2<=len(code)<=50 and CODE.fullmatch(code)):reasons.append('编号须为2–50位字母、数字、_或-');code=''
    if not isinstance(name,str) or not 2<=len(name)<=100:reasons.append('名称须为2–100字');name=''
    if not isinstance(source_note,str) or len(source_note)>300:reasons.append('来源说明须为300字以内文本');source_note=''
    if not isinstance(labels,list) or labels!=list(template.labels):reasons.append('标签顺序须与模板一致：'+' → '.join(template.labels))
    norm=None
    if not isinstance(points,list) or len(points)!=8:reasons.append('须按标签顺序给出8个角点')
    elif all(isinstance(p,list) and len(p)==2 and all(_number(v) for v in p) for p in points):norm=[[float(v) for v in p] for p in points]
    else:reasons.append('每个角点须为[x,y]有限数值，绝对值不超过1e6')
    if code and code in seen:reasons.append('批内编号重复：'+code)
    if code:seen.add(code)
    base={'index':index,'code':code,'name':name,'source_note':source_note,'points':norm}
    if reasons:return {**base,'status':'error','reason':'；'.join(reasons),'changes':[],'specimen_id':None}
    s=existing.get(code)
    if not s:return {**base,'status':'new','reason':'','changes':[],'specimen_id':None}
    changes=[k for k,v in (('name',name),('points',norm),('source_note',source_note)) if getattr(s,k)!=v]
    return {**base,'status':'update' if changes else 'unchanged','reason':'','changes':changes,'specimen_id':s.id}

def preview(db,data,user):
    c=get_collection(db,data.collection_id);t=get_template(db,c.template_id)
    existing={s.code:s for s in list_specimens(db,c.id)};seen=set()
    rows=[validate_row(i,r if isinstance(r,dict) else {},t,existing,seen) for i,r in enumerate(data.rows)]
    counts={k:sum(1 for r in rows if r['status']==k) for k in ('new','update','unchanged','error')}
    current=db.scalar(select(func.count()).select_from(ShapeSpecimen).where(ShapeSpecimen.collection_id==c.id))
    summary={**counts,'total':len(rows),'capacity':{'current':current,'limit':SPECIMEN_LIMIT,'after':current+counts['new'],'sufficient':current+counts['new']<=SPECIMEN_LIMIT}}
    b=IntakeBatch(token=uuid.uuid4().hex,collection_id=c.id,actor=user.email,base_fingerprint=state_fingerprint(db,c),rows=rows,summary=summary,status=IntakeStatus.PREVIEWED)
    db.add(b);db.commit();return b

def confirm(db,token):
    b=db.scalar(select(IntakeBatch).where(IntakeBatch.token==token).with_for_update())
    if not b:raise HTTPException(404,'接收批次不存在')
    if b.status==IntakeStatus.CONFIRMED:return b
    if b.status==IntakeStatus.REJECTED:raise HTTPException(409,b.result.get('reason','批次已整批拒绝，请重新预览'))
    c=get_collection(db,b.collection_id)
    def reject(reason):
        b.status=IntakeStatus.REJECTED;b.result={'reason':reason};b.confirmed_at=datetime.utcnow();db.commit()
        raise HTTPException(409,reason)
    if state_fingerprint(db,c)!=b.base_fingerprint:reject('预览后集合、模板或裁片已被改动，整批拒绝，请重新核对预览')
    new=sum(1 for r in b.rows if r['status']=='new')
    if db.scalar(select(func.count()).select_from(ShapeSpecimen).where(ShapeSpecimen.collection_id==c.id))+new>SPECIMEN_LIMIT:reject(f'集合容量不足（每集合最多{SPECIMEN_LIMIT}份），整批拒绝，请重新核对预览')
    written=[]
    for r in b.rows:
        if r['status']=='new':
            s=ShapeSpecimen(collection_id=c.id,code=r['code'],name=r['name'],points=r['points'],source_note=r['source_note']);db.add(s);db.flush();written.append({'code':r['code'],'action':'created','id':s.id})
        elif r['status']=='update':
            s=db.get(ShapeSpecimen,r['specimen_id']);s.name=r['name'];s.points=r['points'];s.source_note=r['source_note'];written.append({'code':r['code'],'action':'updated','id':s.id})
        elif r['status']=='unchanged':written.append({'code':r['code'],'action':'unchanged','id':r['specimen_id']})
        else:written.append({'code':r['code'] or f"第{r['index']+1}行",'action':'skipped','reason':r['reason']})
    counts={k:sum(1 for w in written if w['action']==k) for k in ('created','updated','unchanged','skipped')}
    b.status=IntakeStatus.CONFIRMED;b.result={'written':written,'counts':counts};b.confirmed_at=datetime.utcnow();db.commit();return b

def list_batches(db,collection_id):return db.scalars(select(IntakeBatch).where(IntakeBatch.collection_id==collection_id).order_by(IntakeBatch.id.desc()).limit(50)).all()
def get_batch(db,token):
    b=db.scalar(select(IntakeBatch).where(IntakeBatch.token==token))
    if not b:raise HTTPException(404,'接收批次不存在')
    return b
