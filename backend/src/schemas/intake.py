from datetime import datetime
from pydantic import BaseModel,Field,ConfigDict
class IntakePreviewInput(BaseModel):
    collection_id:int
    rows:list[dict]=Field(min_length=1,max_length=120)
class IntakeBatchOut(BaseModel):
    id:int
    token:str
    collection_id:int
    actor:str
    status:str
    base_fingerprint:str
    rows:list
    summary:dict
    result:dict
    created_at:datetime
    confirmed_at:datetime|None
    model_config=ConfigDict(from_attributes=True)
