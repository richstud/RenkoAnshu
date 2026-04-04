from pydantic import BaseModel

class XMAccount(BaseModel):
    login: int
    password: str
    server: str
    status: str = "inactive"
