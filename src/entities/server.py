import uuid
from datetime import datetime

from sqlalchemy import UUID, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base import Base


class ServerModel(Base):
    __tablename__ = "servers"

    uuid: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False
    )
    port: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    rcon_port: Mapped[int] = mapped_column(Integer, unique=True, nullable=True)
    rcon_password: Mapped[str] = mapped_column(String, nullable=False)
    version: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), nullable=False
    )

    def __repr__(self):
        return (
            f"<ServerModel(uuid={self.uuid}, ip={self.ip}, port={self.port}, "
            f"version={self.version}, created_at={self.created_at})>"
        )
