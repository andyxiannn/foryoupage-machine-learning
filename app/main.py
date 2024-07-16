from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import auth, post, recommendationRoutes, user
import logging
from logging.handlers import TimedRotatingFileHandler
from log.log_config import RequestFilter
from loguru import logger
from uuid import uuid4
import os
from cronjob.forYouRecommendation import app_forYouRecommendation
from cronjob.popularityRecommendation import app_popularityRecommendation
from middleware.auth import APIKeyMiddleware

app = FastAPI()

origins = [
    settings.CLIENT_ORIGIN,
]

app.add_middleware(APIKeyMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# logging for main application
def correlation_id_filter(record):
    record['correlation_id'] = RequestFilter.correlation_id.get()
    return record['correlation_id']

fmt = "{time:HH:mm:ss.SSS} | {level: <8} | {correlation_id} | {name}:{function}:{line} - {message}"
logger.add("log/wolf-machine-learning.{time:YYYY-MM-DD}.log", format=fmt, level=logging.DEBUG,
           filter=correlation_id_filter, rotation="00:00")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    RequestFilter.correlation_id.set(uuid4().hex)
    response = await call_next(request)
    response.headers["x-request-id"] = RequestFilter.correlation_id.get()
    logger.info(f"{request.method} {request.url} {response.status_code}")
    return response

# app.include_router(auth.router, tags=['Auth'], prefix='/api/auth')
# app.include_router(user.router, tags=['Users'], prefix='/api/users')
# app.include_router(post.router, tags=['Posts'], prefix='/api/posts')
app.include_router(recommendationRoutes.router, tags=['Recommendation'], prefix='/api/data/recommendation')

if settings.CRONJOB_STATUS == "active": 
    app.include_router(app_forYouRecommendation)
    app.include_router(app_popularityRecommendation)
    
@app.get("/api/healthchecker")
def root():
    return {"message": "Welcome to FastAPI with MongoDB"}
