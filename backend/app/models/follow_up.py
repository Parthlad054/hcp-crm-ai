from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey

from app.database import Base


class FollowUp(Base):
    __tablename__ = "follow_ups"

    id = Column(Integer, primary_key=True, index=True)
    interaction_id = Column(Integer, ForeignKey("interactions.id"), nullable=False)
    due_date = Column(Date)
    status = Column(String(50), default="pending")
    note = Column(Text)
