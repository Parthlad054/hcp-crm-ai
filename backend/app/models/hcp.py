from sqlalchemy import Column, Integer, String, Date, Text

from app.database import Base


class HCP(Base):
    __tablename__ = "hcps"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    specialty = Column(String(255))
    hospital_affiliation = Column(String(255))
    last_interaction_date = Column(Date)
    notes = Column(Text)
