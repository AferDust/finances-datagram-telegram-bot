import datetime
import enum
import uuid
from typing import List

from sqlalchemy import (
    ForeignKey,
    Enum,
    text,
    CheckConstraint,
    Integer,
    Boolean,
    String,
    Date,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing_extensions import Annotated

from src.database import Base


positive_integer_field = Annotated[
    int, mapped_column(Integer, CheckConstraint("value >= 0"), default=0)
]
created_at = Annotated[
    datetime.datetime,
    mapped_column(Date, server_default=text("TIMEZONE('utc', now())")),
]
updated_at = Annotated[
    datetime.datetime,
    mapped_column(
        Date,
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=datetime.datetime.utcnow,
    ),
]


class MonthEnum(enum.Enum):
    JANUARY = "January"
    FEBRUARY = "February"
    MARCH = "March"
    APRIL = "April"
    MAY = "May"
    JUNE = "June"
    JULY = "July"
    AUGUST = "August"
    SEPTEMBER = "September"
    OCTOBER = "October"
    NOVEMBER = "November"
    DECEMBER = "December"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    company: Mapped["Company"] = relationship(back_populates="user", uselist=False)


class MonthlyCompanyData(Base):
    __tablename__ = "monthly_companies_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    month: Mapped[MonthEnum] = mapped_column(String, Enum(MonthEnum), nullable=False)
    income: Mapped[positive_integer_field]
    expenses: Mapped[positive_integer_field]
    profit: Mapped[positive_integer_field]
    KPN: Mapped[positive_integer_field]
    created_at: Mapped[created_at]
    company_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )

    company: Mapped["Company"] = relationship(back_populates="monthly_data_set")

    __table_args__ = (
        UniqueConstraint(
            "year", "month", "company_id", name="uix_company_month_year_data"
        ),
    )


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    created_at: Mapped[created_at]
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), unique=True)

    user: Mapped["User"] = relationship(back_populates="company")
    monthly_data_set: Mapped[List["MonthlyCompanyData"]] = relationship(
        back_populates="company", cascade="all, delete-orphan", uselist=True
    )
