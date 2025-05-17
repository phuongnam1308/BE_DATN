from pydantic import BaseModel, constr

class ManualEntry(BaseModel):
    content: constr(min_length=30)
    url: str | None = None