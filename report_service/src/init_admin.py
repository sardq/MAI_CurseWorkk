import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models import UserDB
from src.auth import hash_password


DEFAULT_USERS = [
    {
        "username": os.getenv("ADMIN_USERNAME", "admin"),
        "password": os.getenv("ADMIN_PASSWORD", "admin123"),
        "email": os.getenv("ADMIN_EMAIL", "admin@system.local"),
        "role": "admin",
    },
    {
        "username": os.getenv("OPERATOR_USERNAME", "operator"),
        "password": os.getenv("OPERATOR_PASSWORD", "operator123"),
        "email": os.getenv("OPERATOR_EMAIL", "operator@system.local"),
        "role": "operator",
    },
    {
        "username": os.getenv("USER_USERNAME", "user"),
        "password": os.getenv("USER_PASSWORD", "user123"),
        "email": os.getenv("USER_EMAIL", "user@system.local"),
        "role": "user",
    },
]


async def create_default_admin(db: AsyncSession):
    for u in DEFAULT_USERS:
        result = await db.execute(
            select(UserDB).where(UserDB.username == u["username"])
        )
        existing_user = result.scalar()

        if existing_user:
            continue

        new_user = UserDB(
            username=u["username"],
            hashed_password=hash_password(u["password"]),
            email=u["email"],
            role=u["role"],
            is_active=True,
        )

        db.add(new_user)
        print(f"[INIT] User '{u['username']}' ({u['role']}) created")

    await db.commit()
