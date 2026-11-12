from fastapi import APIRouter,Depends
from src.config.database import get_db
from src.utils.auth import current_user,editor
from src.schemas.intake import IntakePreviewInput,IntakeBatchOut
from src.controllers import intake_controller as controller
router=APIRouter(prefix='/intake',tags=['intake'])
@router.get('',response_model=list[IntakeBatchOut])
def index(collection_id:int,db=Depends(get_db),user=Depends(current_user)):return controller.index(db,collection_id)
@router.get('/{token}',response_model=IntakeBatchOut)
def detail(token:str,db=Depends(get_db),user=Depends(current_user)):return controller.detail(db,token)
@router.post('/preview',response_model=IntakeBatchOut,status_code=201)
def preview(data:IntakePreviewInput,db=Depends(get_db),user=Depends(editor)):return controller.preview(db,data,user)
@router.post('/{token}/confirm',response_model=IntakeBatchOut)
def confirm(token:str,db=Depends(get_db),user=Depends(editor)):return controller.confirm(db,token)
