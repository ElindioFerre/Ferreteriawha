# agent/memory.py — Historial de conversaciones por numero de telefono
import os
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Text, DateTime, select, Integer
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./agentkit.db")
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase): pass

class Mensaje(Base):
    __tablename__ = "mensajes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telefono: Mapped[str] = mapped_column(String(50), index=True)
    role: Mapped[str] = mapped_column(String(20))
    content: Mapped[str] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

async def inicializar_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def guardar_mensaje(telefono: str, role: str, content: str):
    async with async_session() as session:
        session.add(Mensaje(telefono=telefono, role=role, content=content))
        await session.commit()

async def obtener_historial(telefono: str, limite: int = 20) -> list[dict]:
    async with async_session() as session:
        q = select(Mensaje).where(Mensaje.telefono == telefono).order_by(Mensaje.timestamp.desc()).limit(limite)
        r = await session.execute(q)
        msgs = list(reversed(r.scalars().all()))
        return [{"role": m.role, "content": m.content} for m in msgs]

async def limpiar_historial(telefono: str):
    async with async_session() as session:
        r = await session.execute(select(Mensaje).where(Mensaje.telefono == telefono))
        for m in r.scalars().all():
            await session.delete(m)
        await session.commit()
