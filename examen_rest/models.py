from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Laptop(Base):
    __tablename__ = "laptops"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    marca: Mapped[str] = mapped_column(String(100))
    modelo: Mapped[str] = mapped_column(String(100))
    ram_gb: Mapped[int]
    disponible: Mapped[bool] = mapped_column(Boolean, default=True)
