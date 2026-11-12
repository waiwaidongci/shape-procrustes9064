"""Natural-key insert-only shape fixtures, 3 collections x 30 outlines x 8 points."""
import numpy as np
from sqlalchemy import select
from src.config.database import Base,engine,Session
from src.models import User,Template,ShapeCollection,ShapeSpecimen
from src.utils.security import hash_password

def seed():
    Base.metadata.create_all(engine);rng=np.random.default_rng(20261112)
    base=np.array([[0,0],[4,0],[5,.8],[4.5,2.8],[3,4],[1.2,3.5],[-.5,2],[-.7,.6]],dtype=float)*20
    def rotation(a):return np.array([[np.cos(a),-np.sin(a)],[np.sin(a),np.cos(a)]])
    with Session() as db:
        for role,name in [('admin','沈汀 · 复验负责人'),('analyst','林澜 · 形状分析员'),('viewer','叶禾 · 纸模观察员')]:
            email=role+'@tinglan.local'
            if not db.scalar(select(User).where(User.email==email)):db.add(User(email=email,name=name,role=role,password_hash=hash_password('Tinglan2026!')))
        for j,(code,name) in enumerate([('TL-DRIFT','折角展开 · 正常形变集合'),('TL-MIRROR','镜像混入 · 方向核对集合'),('TL-DEGEN','退化角点 · 失败边界集合')]):
            tcode='TL-8-'+str(j+1);t=db.scalar(select(Template).where(Template.code==tcode))
            if not t:t=Template(code=tcode,name='八角点同源基准 '+str(j+1),labels=['L'+str(i+1) for i in range(8)],points=(base@rotation(j*.3)).tolist(),convention='按裁片边界顺序固定L1–L8；不重排、不循环平移、不允许反射；单位mm。');db.add(t);db.flush()
            collection=db.scalar(select(ShapeCollection).where(ShapeCollection.code==code))
            if not collection:collection=ShapeCollection(code=code,name=name,template_id=t.id,protocol='独立裁片的同源角点由上游核对；仅去平移、正尺度与旋转，镜像保留为差异。',source_file=code+'_8landmarks_mm.csv');db.add(collection);db.flush()
            for i in range(30):
                points=base.copy();a=float(rng.normal());b=float(rng.normal());points[2,0]+=a*3;points[3,0]+=a*2;points[4,1]+=b*2.5;points[5,1]+=b*1.5;points+=rng.normal(0,.15,(8,2))
                if j==1 and i in (3,14,25):points[:,0]*=-1
                points=points@rotation(float(rng.uniform(-2.5,2.5)))*float(rng.uniform(.65,1.5))+rng.uniform(-100,100,2)
                if j==2 and i==0:points=np.zeros((8,2))
                scode=f'TL{i+1:02}'
                if not db.scalar(select(ShapeSpecimen).where(ShapeSpecimen.collection_id==collection.id,ShapeSpecimen.code==scode)):db.add(ShapeSpecimen(collection_id=collection.id,code=scode,name='纸模裁片 '+str(i+1).zfill(2),points=points.tolist(),source_note=collection.source_file))
        db.commit()
if __name__=='__main__':seed();print('seed insert-only complete')
