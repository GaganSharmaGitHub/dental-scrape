from fastapi import APIRouter, BackgroundTasks
from jobs.background_tasks import scrape_dental
from model.product_details import ProductDetails
from utils.db import DBTables, database

scrapeRouter = APIRouter(prefix="/scrape-job")


@scrapeRouter.post("/trigger", description="Trigger new scrapping job.")
async def trigger_job(proxy: str, pages: int, background_tasks: BackgroundTasks):
    async def trigger():
        await scrape_dental(pages=pages, proxy=proxy)

    background_tasks.add_task(trigger)
    return {"message": "Scraping job was successfully started."}
