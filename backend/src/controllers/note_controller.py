from src.services import note_service as service
def index(db):return service.list_notes(db)
def create(db,data):return service.create_note(db,data)

def review(db,id,data,user):return service.review_note(db,id,data,user)
def export(db,id):return service.export_note(db,id)
