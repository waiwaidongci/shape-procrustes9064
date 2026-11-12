from fastapi import APIRouter,Depends
from src.config.database import get_db
from src.utils.auth import current_user,editor,admin
from src.schemas.template import TemplateInput,TemplateOut
from src.controllers import template_controller as controller
router=APIRouter(prefix='/templates',tags=['templates'])
@router.get('',response_model=list[TemplateOut])
def index(db=Depends(get_db),user=Depends(current_user)):return controller.index(db)
@router.post('',response_model=TemplateOut,status_code=201)
def create(data:TemplateInput,db=Depends(get_db),user=Depends(editor)):return controller.create(db,data)
@router.put('/{id}',response_model=TemplateOut)
def update(id:int,data:TemplateInput,db=Depends(get_db),user=Depends(editor)):return controller.update(db,id,data)
