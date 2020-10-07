from pydantic import BaseModel
import typing as t
from datetime import date


class AreaBase(BaseModel):
    descricao: str


class AreaCreate(AreaBase):
    area_pai_id: t.Optional[int] = None

    class Config:
        orm_mode = True


class AreaEdit(AreaCreate):
    descricao: t.Optional[str] = None


class Area(AreaBase):
    id: int
    area_pai_id: t.Optional[int] = None

    class Config:
        orm_mode = True


class PessoaAreaCreate(Area):
    descricao: t.Optional[str] = None

    class Config:
        orm_mode = True


class ExperienciaAreaCreate(Area):
    descricao: t.Optional[str] = None

    class Config:
        orm_mode = True


class ProjetoAreaCreate(Area):
    descricao: t.Optional[str] = None

    class Config:
        orm_mode = True