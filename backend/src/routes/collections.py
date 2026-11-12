from fastapi import APIRouter,Depends
from src.config.database import get_db
from src.utils.auth import current_user,editor,admin
from src.schemas.collection import CollectionInput,CollectionOut
from src.controllers import collection_controller as controller
router=APIRouter(prefix='/collections',tags=['collections'])
@router.get('',response_model=list[CollectionOut])
def index(db=Depends(get_db),user=Depends(current_user)):return controller.index(db)
@router.post('',response_model=CollectionOut,status_code=201)
def create(data:CollectionInput,db=Depends(get_db),user=Depends(editor)):return controller.create(db,data)
@router.put('/{id}',response_model=CollectionOut)
def update(id:int,data:CollectionInput,db=Depends(get_db),user=Depends(editor)):return controller.update(db,id,data)
