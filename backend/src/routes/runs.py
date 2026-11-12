from fastapi import APIRouter,Depends
from src.config.database import get_db
from src.utils.auth import current_user,editor,admin
from src.schemas.run import RunInput,RunOut
from src.controllers import run_controller as controller
router=APIRouter(prefix='/runs',tags=['runs'])
@router.get('',response_model=list[RunOut])
def index(db=Depends(get_db),user=Depends(current_user)):return controller.index(db)
@router.post('',response_model=RunOut,status_code=201)
def create(data:RunInput,db=Depends(get_db),user=Depends(editor)):return controller.create(db,data)
@router.get('/{id}',response_model=RunOut)
def detail(id:int,db=Depends(get_db),user=Depends(current_user)):return controller.detail(db,id)
