from sqlalchemy import BigInteger, String, Integer, Boolean, Text, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional, List

from db.models.base import Base, TimestampMixin

class User(Base, TimestampMixin):
    """Модель для зберігання інформації про користувачів"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(32))
    first_name: Mapped[str] = mapped_column(String(64))
    last_name: Mapped[Optional[str]] = mapped_column(String(64))
    language_code: Mapped[Optional[str]] = mapped_column(String(2))

    xp: Mapped[int] = mapped_column(Integer, default=0)
    bonuses: Mapped[int] = mapped_column(Integer, default=0)

    invited_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.user_id"), nullable=True)
    referrals: Mapped[List["User"]] = relationship(
        "User", 
        foreign_keys=[invited_by],
        remote_side="User.user_id", 
        backref="inviter",
        uselist=True
    )

    last_activity: Mapped[datetime] = mapped_column(default=func.now())
    
    def __repr__(self):
        return f"<User {self.user_id} {self.username}>"


class ChatMembership(Base, TimestampMixin):
    """Модель для зберігання членства користувачів в групових чатах"""
    __tablename__ = "chat_memberships"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"))
    chat_id: Mapped[int] = mapped_column(BigInteger)

    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    
    def __repr__(self):
        return f"<ChatMembership user={self.user_id} chat={self.chat_id}>"
