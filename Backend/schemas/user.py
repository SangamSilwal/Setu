from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    nid: str
    age: str
    education: str
    salary: str
    hasDisability: str  # or bool if you convert "yes"/"no"
    disabilityType: Optional[str] = None
    province: str
    district: str
    municipality: str
    ward: str

class Userlogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str