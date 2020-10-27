from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException, status, Form, Response, File, UploadFile
from fastapi.encoders import jsonable_encoder

from app.db.session import get_db
from app.core.security import handle_jwt
from app.core.auth import authenticate_pessoa, sign_up_new_pessoa, get_current_token

import typing as t

from datetime import timedelta, date

from app.db.pessoa import schemas

# from app.tasks import append_refresh_token, check_refresh_token

auth_router = r = APIRouter()


@r.post("/token", response_model=t.Dict[str, schemas.Pessoa], response_model_exclude_none=True)
async def login(
    response: Response,
    db=Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    '''
        Logs user in if authentication data is correct.

        Creates jwt token and append it to response as cookie and can
        only be accessed by HTTP.


        TODO Set secure=True on response.cookie


        Args:
            response: Response to be sent with cookie from fastapi
            db: Database local session
            form_data: dict containing username and password

        Returns:
            A dict in the shape of {"pessoa": schemas.Pessoa}

        Raises:
            HTTPException: Invalid credentials
    '''
    pessoa = await authenticate_pessoa(db, form_data.username, form_data.password)
    try:
        message = pessoa["message"]
    except Exception as e:
        message = False

    if message:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message,
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(
        minutes=handle_jwt.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    if pessoa.superusuario:
        permissions = "admin"
    else:
        permissions = "user"

    serialized_pessoa = {
        "id": pessoa.id, 
        "idealizador": pessoa.idealizador, 
        "aliado": pessoa.aliado, 
        "colaborador": pessoa.colaborador,
        "sub": pessoa.email,
        "permissions": permissions
    }
    access_token = handle_jwt.create_access_token(
        data=serialized_pessoa,
        expires_delta=access_token_expires,
    ).decode('utf-8')
    
    # _refresh_token = handle_jwt.create_refresh_token(
    #     data={"sub": pessoa.email, "permissions": permissions},
    # ).decode('utf-8')

    # append_refresh_token(_refresh_token)
    response.set_cookie(key="jid", value=f"{access_token}", httponly=True)
    # response.set_cookie(key="rjid", value=f"{_refresh_token}", httponly=True)
    return {"pessoa": pessoa}


@r.post("/refresh_token")
async def refresh_token(
    response: Response,
    token=Depends(get_current_token),
    db=Depends(get_db),
):
    credentialsException = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autenticado",
            headers={"WWW-Authenticate": "Bearer"},
    )
    if token:
        return {"access_token":token}
    
    raise credentialsException


@r.post("/logout")
async def logout(response: Response):
    response.set_cookie(key="jid", value="", httponly=True)
    return {"message": "deslogado"}

@r.post("/signup", response_model=t.Dict[str, schemas.Pessoa])
async def signup(
    response: Response,
    db=Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends(),
    email: str = Form(...), telefone: t.Optional[str] = Form(None),
    nome: t.Optional[str] = Form(None), data_nascimento: t.Optional[date] = Form(None),
    foto_perfil: t.Optional[UploadFile] = File(None)
):
    '''
        Sign up user function

        Tries to create a new user account if data sent as FormData
        creates a jwt access token and sets it on cookie, if the
        account already exists, will raise HTTPException.

        Args:
            response: Response to be sent with cookie
            db: Database local session
            form_data: dict containing username and password
            email: Email string
            telefone: Optional phone number as string
            nome: Optional name as string
            data_nascimento: Optional date of birth from datetime.date

        Returns:
            A dict with a message

        Raises:
            HTTPException: status 409 - Account already exists
    '''

    pessoa = await sign_up_new_pessoa(db, usuario=form_data.username,
                                senha=form_data.password, telefone=telefone,
                                nome=nome, email=email,
                                data_nascimento=data_nascimento,
                                foto_perfil=foto_perfil)
    if not pessoa:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conta já existe",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(
        minutes=handle_jwt.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    if pessoa.superusuario:
        permissions = "admin"
    else:
        permissions = "user"

    serialized_pessoa = {
        "id": pessoa.id, 
        "idealizador": pessoa.idealizador, 
        "aliado": pessoa.aliado, 
        "colaborador": pessoa.colaborador,
        "sub": pessoa.email,
        "permissions": permissions
    }

    access_token = handle_jwt.create_access_token(
        data=serialized_pessoa,
        expires_delta=access_token_expires,
    ).decode('utf-8')

    response.set_cookie(key="jid", value=f"{access_token}", httponly=True)

    return {"pessoa": pessoa}
