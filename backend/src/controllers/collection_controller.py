from src.services import collection_service as service
def index(db):return service.list_collections(db)
def create(db,data):return service.create_collection(db,data)

def update(db,id,data):return service.update_collection(db,id,data)
