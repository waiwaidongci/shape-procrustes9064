from src.services import intake_service as service
def index(db,collection_id):return service.list_batches(db,collection_id)
def detail(db,token):return service.get_batch(db,token)
def preview(db,data,user):return service.preview(db,data,user)
def confirm(db,token):return service.confirm(db,token)
