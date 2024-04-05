from pydantic import ConfigDict, BaseModel, Field
from typing import Optional, List


class StudentModel(BaseModel):
    """
    Model for a student record.
    """
    # id: Optional[Annotated[str, BeforeValidator(str)]] = Field(alias="_id", default=None)
    name: str = Field(...)
    age: int = Field(ge=0)
    address: dict = Field(...)
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "name": "string",
                "age": 0,
                "address": {"city": "string", "country": "string"},
            }
        },
    )


class UpdateStudentModel(BaseModel):
    """
    Model for updating a student record.
    """
    name: Optional[str] = None
    age: Optional[int] = None
    address: Optional[dict] = None
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "name": "string",
                "age": 0,
                "address": {"city": "string", "country": "string"},
            }
        },
    )


class StudentListElement(BaseModel):
    """
    Model for a single student record.
    """
    name: str
    age: int


class StudentList(BaseModel):
    """
    Model for a list of student records.
    """
    data: List[StudentListElement]