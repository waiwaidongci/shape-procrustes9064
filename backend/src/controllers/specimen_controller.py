from src.services import specimen_service as service
def index(db,collection_id):return service.list_specimens(db,collection_id)
def create(db,data):return service.create_specimen(db,data)

def update(db,id,data):return service.update_specimen(db,id,data)
