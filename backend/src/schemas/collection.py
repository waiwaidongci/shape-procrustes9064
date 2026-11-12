from pydantic import BaseModel,Field,ConfigDict
class CollectionInput(BaseModel):
    code:str=Field(min_length=2,max_length=40,pattern=r'^[A-Za-z0-9_-]+$')
    name:str=Field(min_length=2,max_length=140)
    template_id:int
    protocol:str=Field(default='',max_length=1200)
    source_file:str=Field(default='',max_length=140)
class CollectionOut(CollectionInput):
    id:int
    model_config=ConfigDict(from_attributes=True)
