import logging
from typing import Union

from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from api.v1.routes import v1Router
from fastapi import Depends, FastAPI, HTTPException, Security, status
import config
from utils.auth import verify_api_key
from utils.db import database
from utils.cache_db import cache_database

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


async def lifespan(app: FastAPI):
    await database.initialize()
    cache_database.initialize()
    yield
    cache_database.terminate()
    await database.terminate()


app = FastAPI(lifespan=lifespan)

app.include_router(v1Router, dependencies=[Depends(verify_api_key)])
