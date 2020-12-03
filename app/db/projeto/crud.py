from fastapi import HTTPException, status, UploadFile
from sqlalchemy.orm import Session
import typing as t
from app.db.habilidade.schemas import PessoaHabilidadeCreate
from app.db.area.schemas import ProjetoAreaCreate

from app.db.utils.salvar_imagem import store_image

from app.db import models
from app.db.utils.extract_areas import append_areas
from app.db.utils.extract_habilidade import append_habilidades
from app.db.utils.salvar_imagem import store_image
from . import schemas
from app.core.security.passwords import get_password_hash

def get_projeto_by_username(db: Session, usuario: str) -> schemas.Projeto:
    return (
        db.query(models.Projeto).filter(models.Projeto.nome == usuario).first()
    )


def get_projeto(db: Session, projeto_id: int) -> schemas.Projeto:
    projeto = db.query(models.Projeto)\
        .filter(models.Projeto.id == projeto_id).first()
    if not projeto:
        raise HTTPException(status_code=404, detail="projeto não encontrado")
    return projeto


def get_projetos(db: Session, skip: int = 0, limit: int = 100) -> t.List[schemas.ProjetoOut]:
    return db.query(models.Projeto).offset(skip).limit(limit).all()

async def edit_projeto(
    db: Session, projeto_id: int, projeto: schemas.ProjetoEdit, pessoa_id: int
) -> schemas.Projeto:

    db_projeto = get_projeto(db, projeto_id)
    if not db_projeto:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail="projeto não encontrado"
        )
    update_data = projeto.dict(exclude_unset=True)

    await append_areas(update_data, db)
    await append_habilidades(update_data, db)

    for key, value in update_data.items():
        setattr(db_projeto, key, value)

    db.add(db_projeto)
    db.commit()
    db.refresh(db_projeto)
    return db_projeto


async def create_projeto(db: Session,
                         nome: str,
                         descricao: str,
                         visibilidade: bool,
                         objetivo: str,
                         foto_capa: t.Optional[UploadFile] = None):

    path = None
    if foto_capa:
        contents = await foto_capa.read()
        path = store_image(contents, foto_capa.filename)
    
    db_projeto = models.Projeto(
        nome=nome,
        descricao=descricao,
        visibilidade=visibilidade,
        objetivo=objetivo,
        foto_capa=path
    )

    db.add(db_projeto)
    db.commit()
    db.refresh(db_projeto)

    db_proj = db_projeto.__dict__
    return {"id": db_proj["id"]}

# async def create_projeto(db: Session, projeto: schemas.ProjetoCreate) -> schemas.Projeto:
#     db_projeto = models.Projeto(
#             nome=projeto.nome,
#             descricao=projeto.descricao,
#             visibilidade=projeto.visibilidade,
#             objetivo=projeto.objetivo
#     )

#     db_proj = projeto.dict(exclude_unset=True)
    
#     await append_areas(db_proj, db)
#     await append_habilidades(db_proj, db)

#     for key, value in db_proj.items():
#         setattr(db_projeto, key, value)

#     db.add(db_projeto)
#     db.commit()
#     db.refresh(db_projeto)
#     return db_projeto


def delete_projeto(db: Session, projeto_id: int):
    projeto = get_projeto(db, projeto_id)
    if not projeto:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail="projeto não encontrado")
    db.delete(projeto)
    db.commit()
    return projeto

def get_habilidades_projeto(db: Session, projeto_id: int):
    projeto = get_projeto(db, projeto_id)
    if not projeto:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail="projeto não encontrada")
    habilidade = projeto.habilidades

    return habilidade

def get_areas_projeto(db: Session, projeto_id: int):
    projeto = get_projeto(db, projeto_id)
    if not projeto:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail="projeto não encontrada")
    area = projeto.areas

    return area