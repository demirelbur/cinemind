from pydantic import BaseModel, ConfigDict


class StrictBaseModel(BaseModel):
    """Base model with strict validation rules shared across CineMind schemas."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )
