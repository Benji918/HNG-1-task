from sqlalchemy import Column, String, Integer, Float
from .database import Base
from datetime import datetime, timezone
import uuid_utils as uuid

def generate_uuid7():
    return str(uuid.uuid7())

def current_time_iso():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(String, primary_key=True, default=generate_uuid7, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    gender = Column(String, nullable=False)
    gender_probability = Column(Float, nullable=False)
    sample_size = Column(Integer, nullable=False)
    age = Column(Integer, nullable=False)
    age_group = Column(String, nullable=False)
    country_id = Column(String, nullable=False)
    country_probability = Column(Float, nullable=False)
    created_at = Column(String, default=current_time_iso, nullable=False)
