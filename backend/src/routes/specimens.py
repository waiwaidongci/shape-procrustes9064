from fastapi import APIRouter,Depends
from src.config.database import get_db
from src.utils.auth import current_user,editor,admin
from src.schemas.specimen import SpecimenInput,SpecimenOut
from src.controllers import specimen_controller as controller
router=APIRouter(prefix='/specimens',tags=['specimens'])
@router.get('',response_model=list[SpecimenOut])
def index(collection_id:int,db=Depends(get_db),user=Depends(current_user)):return controller.index(db,collection_id)
@router.post('',response_model=SpecimenOut,status_code=201)
def create(data:SpecimenInput,db=Depends(get_db),user=Depends(editor)):return controller.create(db,data)
@router.put('/{id}',response_model=SpecimenOut)
def update(id:int,data:SpecimenInput,db=Depends(get_db),user=Depends(editor)):return controller.update(db,id,data)
