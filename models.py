from sqlalchemy import Column, Integer, String, Boolean, Text
from database import Base
from sqlalchemy import DateTime

class Hackathon(Base):
    __tablename__ = "hackathons"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    url = Column(String, nullable=False, unique=True)

    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    registration_deadline = Column(DateTime, nullable=True)

    is_online = Column(Boolean)
    participants_count = Column(Integer)

    themes = Column(Text)

    # Location fields
    city = Column(String)
    state = Column(String)
    country = Column(String)
    location_text = Column(String)

    source = Column(String)

    # 🔥 Unified searchable text field
    search_blob = Column(Text)
