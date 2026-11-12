from src.services import template_service as service
def index(db):return service.list_templates(db)
def create(db,data):return service.create_template(db,data)

def update(db,id,data):return service.update_template(db,id,data)
