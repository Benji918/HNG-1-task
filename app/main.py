from fastapi import FastAPI, Depends, Request, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import models, schemas, crud, services
from .database import engine, get_db

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"status": "error", "message": "Upstream or server failure"})

from fastapi.exceptions import RequestValidationError
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    for error in errors:
        if error.get("type") == "missing" and "name" in error.get("loc", []):
            return JSONResponse(status_code=400, content={"status": "error", "message": "Missing or empty name"})
    return JSONResponse(status_code=422, content={"status": "error", "message": "Invalid type"})


@app.post("/api/profiles", status_code=201)
async def create_profile(profile_in: schemas.ProfileCreate, db: Session = Depends(get_db)):
    if not profile_in.name or not profile_in.name.strip():
        return JSONResponse(status_code=400, content={"status": "error", "message": "Missing or empty name"})
    
    name = profile_in.name.strip().lower()
    
    existing_profile = crud.get_profile_by_name(db, name)
    if existing_profile:
        return {
            "status": "success",
            "message": "Profile already exists",
            "data": existing_profile
        }
    
    try:
        combined_data = await services.get_combined_data(name)
    except services.ExternalAPIException as e:
        return JSONResponse(status_code=e.status_code, content={"status": "error", "message": e.message})
    except Exception as e:
        return JSONResponse(status_code=502, content={"status": "error", "message": "Upstream or server failure"})
    
    created_profile = crud.create_profile(db, combined_data)
    
    return JSONResponse(status_code=201, content={
        "status": "success",
        "data": created_profile
    })

@app.get("/api/profiles/{id}")
def get_profile(id: str, db: Session = Depends(get_db)):
    profile = crud.get_profile(db, id)
    if not profile:
        return JSONResponse(status_code=404, content={"status": "error", "message": "Profile not found"})
    return {
        "status": "success",
        "data": profile
    }

@app.get("/api/profiles")
def get_profiles(gender: str = None, country_id: str = None, age_group: str = None, db: Session = Depends(get_db)):
    profiles = crud.get_profiles(db, gender=gender, country_id=country_id, age_group=age_group)
    return {
        "status": "success",
        "count": len(profiles),
        "data": profiles
    }

@app.delete("/api/profiles/{id}")
def delete_profile(id: str, db: Session = Depends(get_db)):
    success = crud.delete_profile(db, id)
    if not success:
        return JSONResponse(status_code=404, content={"status": "error", "message": "Profile not found"})
    return Response(status_code=204)
