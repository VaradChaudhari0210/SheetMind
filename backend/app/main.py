from fastapi import FastAPI
from app.routes.upload import router as upload_router

app = FastAPI(title = "Datasheet Ingestion Service")

app.include_router(upload_router)

@app.get('/health')
def health_check():
    return {"status" : "ok"}