from datetime import datetime
from sqlalchemy import String,ForeignKey,UniqueConstraint,DateTime,JSON,Double
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class InspectionNote(Base):
    __tablename__='inspection_notes'
    id:Mapped[int]=mapped_column(primary_key=True)
    name:Mapped[str]=mapped_column(String(140),unique=True)
    run_id:Mapped[int]=mapped_column(ForeignKey('alignment_runs.id'))
    specimen_id:Mapped[int]=mapped_column(ForeignKey('shape_specimens.id'))
    protocol:Mapped[str]=mapped_column(String(2000))
    status:Mapped[str]=mapped_column(String(20),default='draft')
    reviewer_note:Mapped[str]=mapped_column(String(1000),default='')
    reviewed_by:Mapped[str]=mapped_column(String(140),default='')
    created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
