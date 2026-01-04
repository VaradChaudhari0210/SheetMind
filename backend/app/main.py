from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routes.upload import router as upload_router
from app.database import engine
from app.models import Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title = "Datasheet Ingestion Service", lifespan=lifespan)

app.include_router(upload_router)

@app.get('/health')
def health_check():
    return {"status" : "ok"}