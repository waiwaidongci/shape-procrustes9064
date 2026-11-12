from sqlalchemy import select
from fastapi import HTTPException
from src.models import ShapeCollection
from src.services.template_service import get_template

def list_collections(db):return db.scalars(select(ShapeCollection).order_by(ShapeCollection.id)).all()
def get_collection(db,id):
    c=db.get(ShapeCollection,id)
    if not c:raise HTTPException(404,'裁片集合不存在')
    return c

def save(db,data,id=None):
    get_template(db,data.template_id)
    if db.scalar(select(ShapeCollection).where(ShapeCollection.code==data.code,ShapeCollection.id!=(id or 0))):raise HTTPException(409,'集合编号重复')
    c=get_collection(db,id) if id else ShapeCollection()
    for k,v in data.model_dump().items():setattr(c,k,v)
    db.add(c);db.commit();return c

def create_collection(db,data):return save(db,data)
def update_collection(db,id,data):return save(db,data,id)
