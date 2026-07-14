from sqlalchemy import (
    Column, Integer, String, Date, Text, Boolean, TIMESTAMP, ForeignKey
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.sql import func

from app.database import Base


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    hcp_id = Column(Integer, ForeignKey("hcps.id"), nullable=False)
    rep_id = Column(String(255))
    interaction_date = Column(Date, nullable=False)
    channel = Column(String(50))                          # in-person / call / email
    topics_discussed = Column(ARRAY(Text))
    products_discussed = Column(ARRAY(Text))
    sentiment = Column(String(50))                        # positive / neutral / negative
    samples_given = Column(JSONB)
    follow_up_required = Column(Boolean, default=False)
    follow_up_date = Column(Date)
    raw_input = Column(Text)                              # original chat / form input
    summary = Column(Text)                                # LLM-generated summary
    source = Column(String(20))                           # form / chat
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
