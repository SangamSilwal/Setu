from fastapi import FastAPI , Request
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings
from db.mongodb import db_instance
from routes import auth 
from contextlib import asynccontextmanager
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

## CORS Setup 
@asynccontextmanager
async def lifespan(app: FastAPI):
    ## Starting logic 
    db_instance.client = AsyncIOMotorClient(settings.mongodb_url)
    print("Succesfully Connected to MongoDB")

    yield

    db_instance.client.close()
    print("MongoDB connection closed")


app = FastAPI(title="FastAPI Mongo Auth",lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials= True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)
app.include_router(auth.router)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print("❌ Validation Error:")
    print(exc.errors())  # This will print in your terminal
    print("📦 Request body:", await request.body())
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )
