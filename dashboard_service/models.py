from pydantic import BaseModel, constr

class ManualEntry(BaseModel):
    content: constr(min_length=30)  # Yêu cầu tối thiểu 30 ký tự
    url: str | None = None