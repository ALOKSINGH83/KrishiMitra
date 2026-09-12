from typing import Literal

from pydantic import BaseModel, Field


class ProfileResponse(BaseModel):
    id: str
    display_name: str | None = None
    phone: str | None = None
    preferred_language: Literal["en", "hi"] = "en"
    role: Literal["farmer", "admin"] = "farmer"
    active: bool = True
class ProfileUpdate(BaseModel):
    display_name: str | None = Field(default=None, max_length=120)
    phone: str | None = Field(default=None, max_length=30)
    preferred_language: Literal["en", "hi"] | None = None
