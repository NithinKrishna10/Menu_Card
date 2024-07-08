from fastcrud import FastCRUD

from ..models.leads import Leads
from ..schemas.leads import LeadsCreate, LeadsUpdate

CRUDLeads = FastCRUD[Leads, LeadsCreate, LeadsUpdate, LeadsUpdate, None]
crud_leads = CRUDLeads(Leads)
