from typing import TYPE_CHECKING

from sqlalchemy import String, Column
from sqlalchemy.orm import relationship, Mapped

from src.adapters.database import Base

if TYPE_CHECKING:
    from .tasks import Consignments


class Products(Base):
    __tablename__ = "products"

    product_id: int = Column(String, primary_key=True, index=True, nullable=False)

    consignments: Mapped[list["Consignments"]] = relationship(
        back_populates="products",
        secondary="products_to_consignments",
        uselist=True,
    )
