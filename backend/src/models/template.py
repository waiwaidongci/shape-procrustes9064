from datetime import datetime
from sqlalchemy import String,ForeignKey,UniqueConstraint,DateTime,JSON,Double
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class Template(Base):
    __tablename__='templates'
    id:Mapped[int]=mapped_column(primary_key=True)
    code:Mapped[str]=mapped_column(String(40),unique=True)
    name:Mapped[str]=mapped_column(String(100))
    labels:Mapped[list]=mapped_column(JSON)
    points:Mapped[list]=mapped_column(JSON)
    convention:Mapped[str]=mapped_column(String(1200),default='')
