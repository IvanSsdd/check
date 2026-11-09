from sqlalchemy import String, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base

class Location(Base):
    __tablename__ = "locations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)

class Employee(Base):
    __tablename__ = "employees"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(200))
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"), index=True)
    location: Mapped[Location] = relationship()

class Shift(Base):
    __tablename__ = "shifts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), index=True)
    started_at: Mapped[object] = mapped_column(DateTime, index=True)
    ended_at: Mapped[object | None] = mapped_column(DateTime, nullable=True, index=True)
    employee: Mapped[Employee] = relationship()

Index("uq_one_open_shift_per_employee", Shift.employee_id, unique=True,
      sqlite_where=Shift.ended_at.is_(None), postgresql_where=Shift.ended_at.is_(None))
