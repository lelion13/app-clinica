from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User, UserRole
from app.schemas.user import UserCreateRequest, UserUpdateRequest


def _parse_role(role: str) -> UserRole:
    try:
        return UserRole(role)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Rol invalido") from exc


def list_users(db: Session) -> list[User]:
    return list(db.execute(select(User).where(User.deleted_at.is_(None)).order_by(User.id)).scalars().all())


def create_user(db: Session, payload: UserCreateRequest, actor_id: int) -> User:
    existing = db.execute(
        select(User).where(User.email == payload.email.lower().strip(), User.deleted_at.is_(None))
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El email ya existe")

    now = datetime.utcnow()
    user = User(
        name=payload.name.strip(),
        email=payload.email.lower().strip(),
        password_hash=hash_password(payload.password),
        role=_parse_role(payload.role),
        is_active=payload.is_active,
        created_at=now,
        updated_at=now,
        created_by=actor_id,
        updated_by=actor_id,
        deleted_at=None,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user_id: int, payload: UserUpdateRequest, actor_id: int) -> User:
    user = db.execute(select(User).where(User.id == user_id, User.deleted_at.is_(None))).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    if payload.name is not None:
        user.name = payload.name.strip()
    if payload.role is not None:
        user.role = _parse_role(payload.role)
    if payload.is_active is not None:
        user.is_active = payload.is_active
    user.updated_at = datetime.utcnow()
    user.updated_by = actor_id

    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int, actor_id: int) -> None:
    user = db.execute(select(User).where(User.id == user_id, User.deleted_at.is_(None))).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    user.deleted_at = datetime.utcnow()
    user.updated_at = datetime.utcnow()
    user.updated_by = actor_id
    db.commit()
