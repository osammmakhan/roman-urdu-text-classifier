from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
import logging
import time
import uuid
from app.config import settings
from app.database import init_db
from app.routes import classification
from app.rate_limiter import limiter


# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    # Clear previous classifications for fresh session
    from app.database import get_db, Classification as ClassificationModel
    db = next(get_db())
    try:
        db.query(ClassificationModel).delete()
        db.commit()
        logger.info("Previous classifications cleared for fresh session")
    finally:
        db.close()
    # Validate API key
    if not settings.groq_api_key:
        logger.warning("GROQ_API_KEY not configured - classification will return neutral")
    yield
    # Shutdown (if needed)


app = FastAPI(
    title="Roman Urdu Text Classifier",
    description="API for classifying Roman Urdu text sentiment",
    version="1.0.0",
    lifespan=lifespan
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    start_time = time.time()
    
    # Log request
    logger.info(
        f"Request started",
        extra={
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "client_ip": request.client.host if request.client else "unknown",
        }
    )
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"Request completed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "status_code": response.status_code,
                "process_time_ms": round(process_time * 1000, 2),
            }
        )
        
        # Add timing header
        response.headers["X-Process-Time"] = str(round(process_time * 1000, 2))
        response.headers["X-Request-ID"] = request_id
        
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"Request failed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "error": str(e),
                "process_time_ms": round(process_time * 1000, 2),
            }
        )
        raise


# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(classification.router)


@app.get("/")
async def root():
    return {"message": "Roman Urdu Text Classifier API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}