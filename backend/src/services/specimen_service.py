from sqlalchemy import select,func
from fastapi import HTTPException
from src.models import ShapeSpecimen
from src.services.collection_service import get_collection

def list_specimens(db,collection_id):return db.scalars(select(ShapeSpecimen).where(ShapeSpecimen.collection_id==collection_id).order_by(ShapeSpecimen.code)).all()
def save(db,data,id=None):
    get_collection(db,data.collection_id)
    if db.scalar(select(ShapeSpecimen).where(ShapeSpecimen.collection_id==data.collection_id,ShapeSpecimen.code==data.code,ShapeSpecimen.id!=(id or 0))):raise HTTPException(409,'集合内裁片编号重复')
    s=db.get(ShapeSpecimen,id) if id else ShapeSpecimen()
    if id and not s:raise HTTPException(404,'裁片不存在')
    if id and s.collection_id!=data.collection_id:raise HTTPException(422,'不能迁移既有裁片所属集合')
    if not id and db.scalar(select(func.count()).select_from(ShapeSpecimen).where(ShapeSpecimen.collection_id==data.collection_id))>=120:raise HTTPException(422,'每集合最多120份裁片')
    for k,v in data.model_dump().items():setattr(s,k,v)
    db.add(s);db.commit();return s

def create_specimen(db,data):return save(db,data)
def update_specimen(db,id,data):return save(db,data,id)
