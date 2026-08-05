from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import JSON
from sqlalchemy import Float

from app.database.base import Base


class Investor(Base):

    __tablename__ = "investors"


    id = Column(
        Integer,
        primary_key=True
    )


    name = Column(
        String,
        nullable=False
    )


    website = Column(
        String
    )


    country = Column(
        String
    )


    investment_stage = Column(
        JSON
    )


    sectors = Column(
        JSON
    )


    ticket_min = Column(
        Float
    )


    ticket_max = Column(
        Float
    )


    confidence_score = Column(
        Float,
        default=0
    )


    sources = Column(
        JSON
    )
