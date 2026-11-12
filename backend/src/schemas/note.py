from pydantic import BaseModel,Field,ConfigDict
from datetime import datetime
from src.constants.enums import NoteStatus
class NoteInput(BaseModel):
    name:str=Field(min_length=2,max_length=140)
    run_id:int
    specimen_id:int
    protocol:str=Field(min_length=10,max_length=2000)
class ReviewInput(BaseModel):
    status:NoteStatus
    reviewer_note:str=Field(min_length=5,max_length=1000)
class NoteOut(NoteInput):
    id:int
    status:str
    reviewer_note:str
    reviewed_by:str
    created_at:datetime
    model_config=ConfigDict(from_attributes=True)
