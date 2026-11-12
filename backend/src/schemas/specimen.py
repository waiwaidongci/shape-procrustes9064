from pydantic import BaseModel,Field,ConfigDict
from src.schemas.template import Outline
class SpecimenInput(BaseModel):
    collection_id:int
    code:str=Field(min_length=2,max_length=50,pattern=r'^[A-Za-z0-9_-]+$')
    name:str=Field(min_length=2,max_length=100)
    points:Outline
    source_note:str=Field(default='',max_length=300)
class SpecimenOut(SpecimenInput):
    id:int
    model_config=ConfigDict(from_attributes=True)
