from fastapi import FastAPI, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect
from app import models
from app.database import Base, engine

from app.routers import upload, report

app = FastAPI(title="s1-report-generator")

inspector = inspect(engine)
existing_tables = inspector.get_table_names()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Hello woeld"}


app.include_router(upload.router)
app.include_router(report.router)

if not existing_tables:
    models.Base.metadata.create_all(bind=engine)
else:
    print("Tables already exist — skipping creation.")
