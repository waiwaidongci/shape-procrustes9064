from pydantic import BaseModel,Field,ConfigDict
from pydantic import model_validator
from typing import Annotated
Coordinate=Annotated[float,Field(strict=True,allow_inf_nan=False,ge=-1e6,le=1e6)]
Point=Annotated[list[Coordinate],Field(min_length=2,max_length=2)]
Outline=Annotated[list[Point],Field(min_length=8,max_length=8)]
Label=Annotated[str,Field(min_length=1,max_length=20)]
class TemplateInput(BaseModel):
    code:str=Field(min_length=2,max_length=40,pattern=r'^[A-Za-z0-9_-]+$')
    name:str=Field(min_length=2,max_length=100)
    labels:list[Label]=Field(min_length=8,max_length=8)
    points:Outline
    convention:str=Field(default='',max_length=1200)
    @model_validator(mode='after')
    def labels_unique(self):
        if len(set(self.labels))!=8:raise ValueError('8个同源角点标签必须唯一')
        return self
class TemplateOut(TemplateInput):
    id:int
    model_config=ConfigDict(from_attributes=True)
