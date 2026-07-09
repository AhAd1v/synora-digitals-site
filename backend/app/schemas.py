from typing import Optional
from pydantic import BaseModel


class SuccessResponse(BaseModel):
    ok: bool = True


class ValidationErrorResponse(BaseModel):
    """Field-addressable so the frontend can call its existing
    showFieldToast(field, msg) with the exact field that failed, the same
    way client-side validation already does."""
    ok: bool = False
    error: str = "validation_error"
    fields: dict[str, str]


class GenericErrorResponse(BaseModel):
    ok: bool = False
    error: str
    message: str
