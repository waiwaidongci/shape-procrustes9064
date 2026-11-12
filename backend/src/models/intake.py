from datetime import datetime
from sqlalchemy import String,ForeignKey,DateTime,JSON
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class IntakeBatch(Base):
    __tablename__='intake_batches'
    id:Mapped[int]=mapped_column(primary_key=True)
    token:Mapped[str]=mapped_column(String(36),unique=True)
    collection_id:Mapped[int]=mapped_column(ForeignKey('shape_collections.id'))
    actor:Mapped[str]=mapped_column(String(160))
    base_fingerprint:Mapped[str]=mapped_column(String(64))
    rows:Mapped[list]=mapped_column(JSON,default=list)
    summary:Mapped[dict]=mapped_column(JSON,default=dict)
    status:Mapped[str]=mapped_column(String(20),default='previewed')
    result:Mapped[dict]=mapped_column(JSON,default=dict)
    created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
    confirmed_at:Mapped[datetime|None]=mapped_column(DateTime,nullable=True)
