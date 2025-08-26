import os
import re
from datetime import timedelta

from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, validator

from app.config import settings
from app.database import get_db
from app.models import User
from app.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user_from_bearer,
)
from app.routers.robots import router as robots_router
from app.routers.maintenance import router as maintenance_router

#  Répertoire contenant le build React (dist/index.html + assets/)
FRONTEND_DIST = os.path.join(os.path.dirname(__file__), "frontend")

app = FastAPI(
    title="API Borobo",
    description="Application téléchargement rapports et maintenance",
)

#  Inclusion des routes d'authentification ---
auth_router = APIRouter(prefix="/auth", tags=["authentification"])

@auth_router.post("/token")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db=Depends(get_db),
):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nom d'utilisateur ou mot de passe incorrect",
        )

    expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": user.username, "role": user.role}
    access_token = create_access_token(data=payload, expires_delta=expires)
    return {"access_token": access_token, "token_type": "bearer"}

@auth_router.get("/users/me")
def read_users_me(current_user: User = Depends(get_current_user_from_bearer)):
    return {"username": current_user.username, "role": current_user.role}

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str
    confirm_password: str

    @validator("new_password")
    def password_complexity(cls, v):
        pattern = re.compile(r"^(?=.*[A-Z])(?=.*\d)(?=.*[!@#\$%\^&\*]).{8,}$")
        if not pattern.match(v):
            raise ValueError(
                "Le mot de passe doit faire au moins 8 caractères, "
                "contenir au moins une majuscule, un chiffre et un caractère spécial"
            )
        return v

    @validator("confirm_password")
    def passwords_match(cls, v, values):
        if "new_password" in values and v != values["new_password"]:
            raise ValueError("Les deux nouveaux mots de passe doivent être identiques")
        return v

@auth_router.post("/users/change-password")
def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user_from_bearer),
    db=Depends(get_db),
):
    if not verify_password(data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ancien mot de passe incorrect",
        )

    current_user.hashed_password = get_password_hash(data.new_password)
    db.add(current_user)
    db.commit()

    return {"detail": "Mot de passe modifié avec succès"}

#  Inclusion des autres routers 
app.include_router(auth_router)
app.include_router(robots_router)
app.include_router(maintenance_router)

#  Montage du frontend React (index.html + assets)
app.mount(
    "/", 
    StaticFiles(directory=FRONTEND_DIST, html=True),
    name="frontend"
)

