from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User, UserRole


def bootstrap_admin(db: Session, name: str, email: str, password: str) -> User:
    users_count = db.execute(select(func.count(User.id)).where(User.deleted_at.is_(None))).scalar_one()
    if users_count > 0:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Setup deshabilitado")

    user = User(
        name=name.strip(),
        email=email.lower().strip(),
        password_hash=hash_password(password),
        role=UserRole.admin,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        created_by=None,
        updated_by=None,
        deleted_at=None,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
