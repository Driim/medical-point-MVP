from pydantic import BaseModel


class User(BaseModel):
    id: str
    name: str
    read: list[str] | None
    write: list[str] | None


class UserCreateDto(BaseModel):
    name: str
    read: list[str] | None
    write: list[str] | None


class UserAddReadAccessDto(BaseModel):
    read: list[str]


class UserAddWriteAccessDto(BaseModel):
    write: list[str]
