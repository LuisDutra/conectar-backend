from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException, status, Form
from datetime import timedelta

from app.db.session import get_db
from app.core import security
from app.core.auth import authenticate_pessoa, sign_up_new_pessoa

from typing import Optional

auth_router = r = APIRouter()


@r.post("/token")
async def login(
    db=Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    pessoa = authenticate_pessoa(db, form_data.username, form_data.password)
    if not pessoa:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(
        minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    if pessoa.is_superuser:
        permissions = "admin"
    else:
        permissions = "user"
    access_token = security.create_access_token(
        data={"sub": pessoa.email, "permissions": permissions},
        expires_delta=access_token_expires,
    )

    return {"access_token": access_token, "token_type": "bearer"}


@r.post("/signup")
async def signup(
    db=Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends(),
    email: str = Form(...), telefone: Optional[str] = Form(...), nome: Optional[str] = Form(...)
):
    pessoa = sign_up_new_pessoa(db, username=form_data.username,
                                password=form_data.password, telefone=telefone,
                                nome=nome, email=email)
    if not pessoa:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Account already exists",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(
        minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    if pessoa.is_superuser:
        permissions = "admin"
    else:
        permissions = "user"
    access_token = security.create_access_token(
        data={"sub": pessoa.email, "permissions": permissions},
        expires_delta=access_token_expires,
    )

    return {"access_token": access_token, "token_type": "bearer"}
