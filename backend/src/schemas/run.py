from pydantic import BaseModel,Field,ConfigDict
from datetime import datetime
class RunInput(BaseModel):
    name:str=Field(min_length=2,max_length=140)
    collection_id:int
    retained:int=Field(default=3,ge=1,le=5,strict=True)
    tolerance:float=Field(default=1e-12,ge=1e-14,le=1e-6,allow_inf_nan=False,strict=True)
class RunOut(RunInput):
    id:int
    status:str
    snapshot:dict
    result:dict
    error:str
    created_at:datetime
    model_config=ConfigDict(from_attributes=True)
