from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import BigInteger, func
from sqlalchemy.ext.asyncio import AsyncAttrs
from datetime import datetime
from typing import Optional

class Base(AsyncAttrs, DeclarativeBase):
    """Базовий клас для всіх моделей"""
    pass

class TimestampMixin:
    """Міксін для відстеження часу створення та оновлення записів"""
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
