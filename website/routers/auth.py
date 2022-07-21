import uuid, jwt, time

from typing import Optional, Dict
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi import APIRouter, Depends, HTTPException, status, Security, Request, Response, Form
from fastapi.security import OAuth2PasswordRequestForm, SecurityScopes, OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.hash import bcrypt
from fastapi.responses import HTMLResponse

from website.internal import models, schemas, crud
from website.internal.database import get_session

auth = APIRouter()
templates = Jinja2Templates(directory="website/templates")


class OAuth2PasswordBearerWithCookie(OAuth2):
    def __init__(
            self,
            tokenUrl: str,
            scheme_name: Optional[str] = None,
            scopes: Optional[Dict[str, str]] = None,
            auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.cookies.get("access_token")  # changed to accept access token from httpOnly Cookie

        scheme, param = get_authorization_scheme_param(authorization)
        # if not authorization or scheme.lower() != "bearer":
        #     if self.auto_error:
        #         raise HTTPException(
        #             status_code=status.HTTP_401_UNAUTHORIZED,
        #             detail="Not authenticated",
        #             headers={"WWW-Authenticate": "Bearer"},
        #         )
        #     else:
        #         return None
        return param


oauth2_scheme = OAuth2PasswordBearerWithCookie(
    tokenUrl='auth/login-user',
    scopes={'me': 'Read information about the current user.', 'admin': 'Fetch problem list and add contests.'}
)
JWT_SECRET = '01e40851a7d55710066b587804f0094197441cfdd2bf931b7abf7318cb05edaf'
JWT_ALG = "HS256"
JWT_EXPIRE_SECONDS = 10800


async def get_user_from_token(
        db: AsyncSession = Depends(get_session),
        token: str = Depends(oauth2_scheme)
) -> Optional[schemas.User]:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        username = payload.get('sub')
        user = await crud.get_user_by_username(db, username)
        return user
    except:
        # database errors, jwt errors, no token errors
        return None


async def get_scopes_from_token(
        token: str = Depends(oauth2_scheme)
) -> Optional[list[str]]:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        token_scopes = payload.get('scopes', [])
        return token_scopes
    except:
        return None


async def get_current_user_required(
        security_scopes: SecurityScopes,
        user: Optional[schemas.User] = Depends(get_user_from_token),
        scopes: Optional[list[str]] = Depends(get_scopes_from_token)
) -> schemas.User:
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="An authorized user is required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if security_scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = f'Bearer'
    for scope in security_scopes.scopes:
        if scope not in scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )

    return user


async def get_current_user_optional(
        user: Optional[schemas.User] = Depends(get_user_from_token)
) -> Optional[schemas.User]:
    return user


async def change_password(
        db: AsyncSession,
        user: schemas.UserUpdate
) -> schemas.User:
    this_user = await crud.get_user_by_username(db, user.username)
    if not this_user:
        # what the fuck
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="User does not exist",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not bcrypt.verify(user.old_password, this_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if len(user.new_password) < 7:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must be at least 8 characters",
        )
    # TODO: more internal checks
    updated_user = schemas.UserUpdate(username=user.username, new_password=bcrypt.hash(user.new_password), old_password="")
    user_info = await crud.update_user(db, updated_user)
    return user_info


async def login_user(
        db: AsyncSession,
        username: str,
        password: str
) -> schemas.User:
    user = await crud.get_user_by_username(db, username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="User does not exist",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not bcrypt.verify(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def signup_user(
        db: AsyncSession,
        user: schemas.UserCreate
) -> schemas.User:
    temp_user = await crud.get_user_by_username(db, user.username)
    if temp_user:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="User already exists",
        )
    if len(user.username) < 2:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Username must be at least 3 characters",
        )
    if len(user.password) < 7:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must be at least 8 characters",
        )
    # TODO: other internal checks
    user_uuid = str(uuid.uuid4())
    user = schemas.UserCreate(username=user.username, password=bcrypt.hash(user.password))
    new_user = await crud.create_user(db, user, user_uuid)
    return new_user


@auth.post('/auth/change-password')
async def change_password_of_user(
        username: str = Form(),
        old_password: str = Form(),
        new_password: str = Form(),
        current_user: schemas.User = Security(get_current_user_required, scopes=['me']),
        db: AsyncSession = Depends(get_session)
):
    user_info = schemas.UserUpdate(username=username, old_password=old_password, new_password=new_password)
    updated_user = await change_password(db, user_info)
    return updated_user


@auth.post('/auth/login-user')
async def login_user_for_access_token(
        response: Response,
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_session)
):
    await login_user(db, form_data.username, form_data.password)
    scopes = ["me"]
    if (form_data.username) == "admin":
        scopes.append("admin")
    token_info = schemas.Token(
        iss="usacochecklist",
        sub=form_data.username,
        iat=int(time.time()),
        exp=int(time.time() + JWT_EXPIRE_SECONDS),
        jti=str(uuid.uuid4()),
        scopes=scopes
    )
    access_token = jwt.encode(token_info.dict(), JWT_SECRET)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True, samesite="strict")
    return {'access_token': access_token, 'token_type': 'bearer'}


@auth.post('/auth/signup-user', response_model=schemas.User)
async def signup_user_to_database(
        username: str = Form(),
        password: str = Form(),
        db: AsyncSession = Depends(get_session)
):
    user_info = schemas.UserCreate(username=username, password=password)
    new_user = await signup_user(db, user_info)
    return new_user


@auth.post('/auth/logout-user')
async def logout_user(
        response: Response,
        current_user: schemas.User = Security(get_current_user_required, scopes=['me'])
):
    response.delete_cookie("access_token")
    return


@auth.get('/change-password', response_class=HTMLResponse)
async def password_page(
        request: Request,
        current_user: schemas.User = Security(get_current_user_required, scopes=['me'])
):
    return templates.TemplateResponse("change-password.html", {'request': request, 'user': current_user})


@auth.get('/login', response_class=HTMLResponse)
async def login_page(
        request: Request,
        current_user: schemas.User = Depends(get_current_user_optional)
):
    return templates.TemplateResponse("login.html", {'request': request, 'user': current_user})


@auth.get('/signup', response_class=HTMLResponse)
async def signup_page(
        request: Request,
        current_user: schemas.User = Depends(get_current_user_optional)
):
    return templates.TemplateResponse("signup.html", {'request': request, 'user': current_user})
