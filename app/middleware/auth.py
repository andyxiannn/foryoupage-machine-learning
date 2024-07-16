from fastapi import FastAPI, Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.config import settings
from app.response_model.common_model import errorHandler, successHandler, IncorrectCredentialsError

# Define a middleware class for API key verification
class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            api_key = request.headers.get("X-API-KEY")
            if not api_key or api_key != settings.API_KEY:
                raise IncorrectCredentialsError("Unauthorized")
            response = await call_next(request)
            return response
        except Exception as e: 
            return errorHandler(e)