from fastapi import APIRouter
from api.v1.scrape_jobs import scrapeRouter
v1Router = APIRouter(prefix="/api/v1")
v1Router.include_router(scrapeRouter)