from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


def uuid_col() -> str:
    return str(uuid4())


class Profile(Base):
    __tablename__ = "profiles"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    display_name: Mapped[str | None] = mapped_column(String(120))
    phone: Mapped[str | None] = mapped_column(String(30))
    preferred_language: Mapped[str] = mapped_column(String(2), default="en", nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="farmer", nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    farms: Mapped[list["Farm"]] = relationship(back_populates="owner")


class Farm(Base):
    __tablename__ = "farms"
    __table_args__ = (CheckConstraint("area > 0", name="farms_area_positive"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_col)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("profiles.id", ondelete="RESTRICT"), index=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    village: Mapped[str | None] = mapped_column(String(120))
    district: Mapped[str] = mapped_column(String(120), nullable=False)
    state: Mapped[str] = mapped_column(String(120), nullable=False)
    pincode: Mapped[str | None] = mapped_column(String(10))
    latitude: Mapped[float | None]
    longitude: Mapped[float | None]
    area: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), default="acre", nullable=False)
    soil_type: Mapped[str | None] = mapped_column(String(80))
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    owner: Mapped[Profile] = relationship(back_populates="farms")
    crops: Mapped[list["Crop"]] = relationship(back_populates="farm")
    soil_readings: Mapped[list["SoilReading"]] = relationship(back_populates="farm")


class Crop(Base):
    __tablename__ = "crops"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_col)
    farm_id: Mapped[str] = mapped_column(String(36), ForeignKey("farms.id", ondelete="RESTRICT"), index=True)
    crop_code: Mapped[str] = mapped_column(String(40), nullable=False)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    variety: Mapped[str | None] = mapped_column(String(80))
    sowing_date: Mapped[date] = mapped_column(Date, nullable=False)
    growth_stage: Mapped[str] = mapped_column(String(30), nullable=False)
    expected_harvest_date: Mapped[date | None] = mapped_column(Date)
    area: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    farm: Mapped[Farm] = relationship(back_populates="crops")


class SoilReading(Base):
    __tablename__ = "soil_readings"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_col)
    farm_id: Mapped[str] = mapped_column(String(36), ForeignKey("farms.id", ondelete="RESTRICT"), index=True)
    source: Mapped[str] = mapped_column(String(20), nullable=False)
    moisture: Mapped[float | None]
    ph: Mapped[float | None]
    nitrogen: Mapped[float | None]
    phosphorus: Mapped[float | None]
    potassium: Mapped[float | None]
    temperature_c: Mapped[float | None]
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    farm: Mapped[Farm] = relationship(back_populates="soil_readings")


class IdempotencyKey(Base):
    __tablename__ = "idempotency_keys"
    __table_args__ = (UniqueConstraint("user_id", "key", "operation", name="uq_idempotency_user_key_operation"),)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("profiles.id", ondelete="RESTRICT"), primary_key=True)
    key: Mapped[str] = mapped_column(String(255), primary_key=True)
    operation: Mapped[str] = mapped_column(String(80), primary_key=True)
    response_id: Mapped[str | None] = mapped_column(String(36))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
