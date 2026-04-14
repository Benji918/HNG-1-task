from sqlalchemy.orm import Session
from . import models

def to_dict(obj):
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}

def get_profile_by_name(db: Session, name: str):
    obj = db.query(models.Profile).filter(models.Profile.name == name).first()
    return to_dict(obj) if obj else None

def get_profile(db: Session, profile_id: str):
    obj = db.query(models.Profile).filter(models.Profile.id == profile_id).first()
    return to_dict(obj) if obj else None

def create_profile(db: Session, profile_data: dict):
    db_profile = models.Profile(**profile_data)
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return to_dict(db_profile)

def get_profiles(db: Session, gender: str = None, country_id: str = None, age_group: str = None):
    query = db.query(models.Profile)
    if gender:
        query = query.filter(models.Profile.gender.ilike(gender))
    if country_id:
        query = query.filter(models.Profile.country_id.ilike(country_id))
    if age_group:
        query = query.filter(models.Profile.age_group.ilike(age_group))
    
    return [{
        "id": c.id,
        "name": c.name,
        "gender": c.gender,
        "age": c.age,
        "age_group": c.age_group,
        "country_id": c.country_id
    } for c in query.all()]

def delete_profile(db: Session, profile_id: str):
    db_profile = db.query(models.Profile).filter(models.Profile.id == profile_id).first()
    if db_profile:
        db.delete(db_profile)
        db.commit()
        return True
    return False
