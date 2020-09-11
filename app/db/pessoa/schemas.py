from pydantic import BaseModel
import typing as t
from datetime import date


class PessoaBase(BaseModel):
    senha: str
    data_nascimento: t.Optional[date] = None
    email: str
    ativo: bool = True
    nome: t.Optional[str] = None
    telefone: t.Optional[str] = None
    colaborador: t.Optional[bool] = None
    idealizador: t.Optional[bool] = None
    aliado: t.Optional[bool] = None

class PessoaOut(PessoaBase):
    pass


class PessoaCreate(PessoaBase):
    superusuario: t.Optional[bool] = False
    usuario: str

    class Config:
        orm_mode = True


class PessoaEdit(PessoaBase):
    senha: t.Optional[str] = None
    email: t.Optional[str] = None

    class Config:
        orm_mode = True


class Pessoa(PessoaBase):
    id: int

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str = None
    permission: str = "user"