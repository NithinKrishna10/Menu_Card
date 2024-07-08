from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

class LeadsBase(BaseModel):
    name : str | None
    place : str | None
    contact : str | None
    franchise : int | None
    price : int | None
    

class LeadsCreate(LeadsBase):
    pass

class LeadsUpdate(LeadsBase):
    pass

class LeadsRead(LeadsBase):
    id : int