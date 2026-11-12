from datetime import datetime
from sqlalchemy import String,ForeignKey,UniqueConstraint,DateTime,JSON,Double
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class ShapeSpecimen(Base):
    __tablename__='shape_specimens'
    id:Mapped[int]=mapped_column(primary_key=True)
    collection_id:Mapped[int]=mapped_column(ForeignKey('shape_collections.id'))
    code:Mapped[str]=mapped_column(String(50))
    name:Mapped[str]=mapped_column(String(100))
    points:Mapped[list]=mapped_column(JSON)
    source_note:Mapped[str]=mapped_column(String(300),default='')
    __table_args__=(UniqueConstraint('collection_id','code'),)
