from sqlalchemy import select
from fastapi import HTTPException
from src.models import Template

def list_templates(db):return db.scalars(select(Template).order_by(Template.id)).all()
def get_template(db,id):
    t=db.get(Template,id)
    if not t:raise HTTPException(404,'同源模板不存在')
    return t

def save(db,data,id=None):
    if db.scalar(select(Template).where(Template.code==data.code,Template.id!=(id or 0))):raise HTTPException(409,'模板编号重复')
    t=get_template(db,id) if id else Template()
    for k,v in data.model_dump().items():setattr(t,k,v)
    db.add(t);db.commit();return t

def create_template(db,data):return save(db,data)
def update_template(db,id,data):return save(db,data,id)
