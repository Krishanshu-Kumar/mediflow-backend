from pydantic import BaseModel, ConfigDict


class MasterCodeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: int
    category_code: int
    value: str
    display_name: str
    is_active: bool
