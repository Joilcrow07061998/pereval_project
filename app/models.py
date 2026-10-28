from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    fam: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))
    otc: Mapped[str | None] = mapped_column(String(100), nullable=True)
    phone: Mapped[str] = mapped_column(String(30))

    passes: Mapped[list["MountainPass"]] = relationship(back_populates="user")


class MountainPass(Base):
    __tablename__ = "mountain_passes"

    id: Mapped[int] = mapped_column(primary_key=True)
    beauty_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    title: Mapped[str] = mapped_column(String(255))
    other_titles: Mapped[str | None] = mapped_column(Text, nullable=True)
    connect: Mapped[str | None] = mapped_column(Text, nullable=True)
    add_time: Mapped[str] = mapped_column(String(50))
    date_added: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    status: Mapped[str] = mapped_column(String(20), default="new", server_default="new", index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))

    user: Mapped[User] = relationship(back_populates="passes")
    coordinates: Mapped["Coordinates"] = relationship(back_populates="mountain_pass", cascade="all, delete-orphan", uselist=False)
    level: Mapped["PassLevel"] = relationship(back_populates="mountain_pass", cascade="all, delete-orphan", uselist=False)
    images: Mapped[list["PassImage"]] = relationship(back_populates="mountain_pass", cascade="all, delete-orphan")


class Coordinates(Base):
    __tablename__ = "pass_coordinates"

    id: Mapped[int] = mapped_column(primary_key=True)
    pass_id: Mapped[int] = mapped_column(ForeignKey("mountain_passes.id", ondelete="CASCADE"), unique=True)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    height: Mapped[int] = mapped_column(Integer)

    mountain_pass: Mapped[MountainPass] = relationship(back_populates="coordinates")


class PassLevel(Base):
    __tablename__ = "pass_levels"

    id: Mapped[int] = mapped_column(primary_key=True)
    pass_id: Mapped[int] = mapped_column(ForeignKey("mountain_passes.id", ondelete="CASCADE"), unique=True)
    winter: Mapped[str | None] = mapped_column(String(20), nullable=True)
    summer: Mapped[str | None] = mapped_column(String(20), nullable=True)
    autumn: Mapped[str | None] = mapped_column(String(20), nullable=True)
    spring: Mapped[str | None] = mapped_column(String(20), nullable=True)

    mountain_pass: Mapped[MountainPass] = relationship(back_populates="level")


class PassImage(Base):
    __tablename__ = "pass_images"

    id: Mapped[int] = mapped_column(primary_key=True)
    pass_id: Mapped[int] = mapped_column(ForeignKey("mountain_passes.id", ondelete="CASCADE'), index=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    data: Mapped[str] = mapped_column(Text)

    mountain_pass: Mapped[MountainPass] = relationship(back_populates="images")
