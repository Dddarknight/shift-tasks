from datetime import date, datetime

from sqlalchemy import Column, Boolean, String, Integer, Date, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, relationship

from src.adapters.database import Base
from src.db_models.products import Products


class Consignments(Base):
    __tablename__ = "consignments"

    consignment_id: int = Column(Integer, primary_key=True, index=True, nullable=False)
    consignment_number: int = Column(Integer, nullable=False)
    consignment_date: date = Column(Date, nullable=False)

    tasks: Mapped[list["ShiftTasks"]] = relationship(
        back_populates="consignment",
        uselist=True,
    )
    products: Mapped[list["Products"]] = relationship(
        back_populates="consignments",
        secondary="products_to_consignments",
        uselist=True,
    )

    __table_args__ = (
            UniqueConstraint('consignment_number',
                             'consignment_date'),)


class ShiftTasks(Base):
    __tablename__ = "shift_tasks"

    task_id: int = Column(Integer, primary_key=True, index=True, nullable=False)
    close_status: bool = Column(Boolean)
    name: str = Column(String)
    line: str = Column(String)
    shift: str = Column(String)
    brigade: str = Column(String)
    nomenclature: str = Column(String)
    code: str = Column(String)
    identifier: str = Column(String)
    started_at: datetime = Column(DateTime)
    completed_at: datetime = Column(DateTime)
    consignment_id: int = Column(Integer, ForeignKey(Consignments.consignment_id), nullable=False)
    closed_at: datetime = Column(DateTime)

    consignment: Mapped["Consignments"] = relationship(
        back_populates="tasks",
    )


class ProductsToConsignments(Base):
    __tablename__ = "products_to_consignments"

    product_to_consignment_id: int = Column(Integer, primary_key=True, nullable=False)
    product_id: str = Column(String, ForeignKey(Products.product_id), nullable=False)
    consignment_id: int = Column(Integer, ForeignKey(Consignments.consignment_id), nullable=False)
    is_aggregated: bool = Column(Boolean, default=False)
    aggregated_at: datetime = Column(DateTime, default=None)
