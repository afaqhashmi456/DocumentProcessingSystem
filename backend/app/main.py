import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.api.routes import router
from app.config.settings import settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Document Processing Api")
    logger.info(f"APi Version: {settings.api_version}")
    logger.info(f"CSV Path: {settings.csv_path}")
    logger.info(f"Upload Directory: {settings.upload_dir}")
    yield
    
    logger.info("Shutting down Document Processing Api")


app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    lifespan=lifespan,
)

cors_origins = settings.cors_origins.split(',')
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info(f"CORS enabled for origins: {cors_origins}")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred while processing your request",
            "details": str(exc) if settings.api_version.startswith("dev") else None
        }
    )

app.include_router(router, prefix="/api")

@app.get("/")
async def root():
    return {
        "name": settings.api_title,
        "version": settings.api_version,
        "description": settings.api_description,
        "endpoints": {
            "health": "/api/health",
            "process": "/api/process (POST)"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting development server...")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
