from fastapi import APIRouter,Depends
from src.config.database import get_db
from src.utils.auth import current_user,editor,admin
from src.schemas.note import NoteInput,NoteOut
from src.controllers import note_controller as controller
router=APIRouter(prefix='/notes',tags=['notes'])
@router.get('',response_model=list[NoteOut])
def index(db=Depends(get_db),user=Depends(current_user)):return controller.index(db)
@router.post('',response_model=NoteOut,status_code=201)
def create(data:NoteInput,db=Depends(get_db),user=Depends(editor)):return controller.create(db,data)
from fastapi.responses import Response
from src.schemas.note import ReviewInput
@router.post('/{id}/review',response_model=NoteOut)
def review(id:int,data:ReviewInput,db=Depends(get_db),user=Depends(admin)):return controller.review(db,id,data,user)
@router.get('/{id}/export')
def export(id:int,db=Depends(get_db),user=Depends(current_user)):return Response(controller.export(db,id),media_type='text/csv; charset=utf-8',headers={'Content-Disposition':f'attachment; filename="inspection-note-{id}.csv"'})
