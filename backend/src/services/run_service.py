import json
from pathlib import Path
from sqlalchemy import select,func
from fastapi import HTTPException
from redis import Redis
from src.config.settings import REDIS_URL
from src.models import AlignmentRun
from src.services.collection_service import get_collection
from src.services.template_service import get_template
from src.services.specimen_service import list_specimens
from src.services.deformation import analyze_alignment
from src.constants.enums import RunStatus
redis=Redis.from_url(REDIS_URL)
def list_runs(db):return db.scalars(select(AlignmentRun).order_by(AlignmentRun.id.desc())).all()
def get_run(db,id):
    r=db.get(AlignmentRun,id)
    if not r:raise HTTPException(404,'对齐研究不存在')
    return r

def create_run(db,data):
    c=get_collection(db,data.collection_id);t=get_template(db,c.template_id)
    if db.scalar(select(AlignmentRun).where(AlignmentRun.name==data.name)):raise HTTPException(409,'研究名称重复')
    if db.scalar(select(func.count()).select_from(AlignmentRun).where(AlignmentRun.status.in_(['queued','running'])))>=3:raise HTTPException(429,'已有3项活动任务，请等待')
    snapshot={'collection':{k:getattr(c,k) for k in ('id','code','name','protocol','source_file','template_id')},'template':{k:getattr(t,k) for k in ('id','code','name','labels','points','convention')},'specimens':[{k:getattr(s,k) for k in ('id','code','name','points','source_note')} for s in list_specimens(db,c.id)]}
    r=AlignmentRun(**data.model_dump(),snapshot=snapshot,status=RunStatus.QUEUED);db.add(r);db.commit()
    try:redis.lpush('shapes:runs',str(r.id))
    except Exception:pass
    return r

def execute_run(db,id):
    r=get_run(db,id)
    if r.status not in (RunStatus.QUEUED,RunStatus.RUNNING):return
    r.status=RunStatus.RUNNING;db.commit()
    try:
        result=analyze_alignment(r.snapshot,r.retained,r.tolerance);Path('/artifacts').mkdir(exist_ok=True);Path(f'/artifacts/run-{id}.json').write_text(json.dumps(result,ensure_ascii=False,allow_nan=False));r.result=result;r.status=RunStatus.COMPLETED;r.error='';db.commit()
    except Exception as exc:
        db.rollback();r=get_run(db,id);r.status=RunStatus.FAILED;r.error=str(exc)[:600];db.commit()
