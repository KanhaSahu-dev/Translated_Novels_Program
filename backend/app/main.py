from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from loguru import logger

from app.api import scraper_routes, nlp_routes, glossary_routes
from app.models.database import init_database

# Initialize FastAPI app
app = FastAPI(
    title="Novel Translation Refiner",
    description="API for extracting and refining machine-translated novel text",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Angular dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
@app.on_event("startup")
async def startup_event():
    await init_database()
    logger.info("Database initialized successfully")

# Include routers
app.include_router(scraper_routes.router, prefix="/api/scraper", tags=["scraper"])
app.include_router(nlp_routes.router, prefix="/api/nlp", tags=["nlp"])
app.include_router(glossary_routes.router, prefix="/api/glossary", tags=["glossary"])

@app.get("/")
async def root():
    return {"message": "Novel Translation Refiner API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running normally"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    ) 