import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models import UserDB
from src.auth import hash_password

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@system.local")


async def create_default_admin(db: AsyncSession):
    """
    Создаёт администратора при первом запуске приложения,
    если он ещё не существует.
    """

    result = await db.execute(
        select(UserDB).where(UserDB.username == ADMIN_USERNAME)
    )
    admin = result.scalar()

    if admin:
        return  # Администратор уже существует

    admin_user = UserDB(
        username=ADMIN_USERNAME,
        hashed_password=hash_password(ADMIN_PASSWORD),
        email=ADMIN_EMAIL,
        role="admin",
        is_active=True
    )

    db.add(admin_user)
    await db.commit()

    print(f"[INIT] Admin user '{ADMIN_USERNAME}' created")
