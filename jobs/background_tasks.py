from asyncio import sleep
import json
import logging
from bs4 import BeautifulSoup
import requests
import re
from config import SITE_TO_BE_SCRAPED, ALLOWED_RETRY_ATTEMPTS, RETRY_TIMEOUT
from utils.db import DBTables, database
from utils.cache_db import cache_database
from model.product_details import ProductDetails
from utils.notifications import notify_user
from utils.storage import upload_file_from_link
from utils.string_utils import extract_float, get_last_part_of_url


async def scrape_dental(pages: int, proxy: str, retry_attempt: int = 0):
    try:
        metrics = {
            "from_cache": 0,
        }
        db_to_upserts = []
        request_proxies = {
            "http": proxy,
            "https": proxy,
        }
        for page_no in range(1, pages + 1):
            logging.info(f"Processing page #{page_no}")
            response = requests.get(
                f"{SITE_TO_BE_SCRAPED}{page_no}/", proxies=request_proxies
            )
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                for product_cards in soup.select("div.product-inner"):
                    product_image = product_cards.select_one(
                        "img.attachment-woocommerce_thumbnail"
                    )
                    image_url = product_image.get("data-lazy-src")
                    product_title = product_image.get("title")
                    product_price = 0
                    # maybe for future where id is needed
                    product_id = get_last_part_of_url(
                        product_cards.select("a")[0].get("href")
                    )
                    prices = product_cards.select("span.price span.amount")
                    for price in prices:
                        if not price.find_parent("del"):
                            product_price = extract_float(price.get_text())
                    product_details = ProductDetails(
                        product_price=product_price,
                        product_title=product_title,
                        path_to_image="",
                    )
                    cached_data = await cache_database.get_value(
                        f"{DBTables.dental_product_details}/{product_title}"
                    )
                    if cached_data and (
                        float(cached_data) == product_details.product_price
                    ):
                        logging.info(f"Data is already cached for {product_title}")
                        metrics["from_cache"] = metrics["from_cache"] + 1
                    else:
                        logging.info(f"Saving fresh data for {product_title}")
                        product_details.path_to_image = upload_file_from_link(image_url)
                        await cache_database.set_value(
                            f"{DBTables.dental_product_details}/{product_title}",
                            product_details.product_price,
                        )
                        db_to_upserts.append(
                            (
                                {"product_title": product_details.product_title},
                                product_details.model_dump(),
                            )
                        )
                    logging.info(f"{product_title}")

            else:
                logging.info(
                    f"Failed to retrieve the webpage. Status code: {response.status_code}"
                )
        if len(db_to_upserts) > 0:
            db_metrics = await database.upsert_many_records(
                DBTables.dental_product_details, db_to_upserts
            )
            metrics.update(db_metrics)
        notify_user(title="Data scraping successful", data=metrics)
    except Exception as e:
        logging.error(f"Failed to scrape data in attempt #{retry_attempt} {e}")
        if retry_attempt >= ALLOWED_RETRY_ATTEMPTS:
            logging.info("Retry attempts exhausted")
            notify_user("Unable to scrape site data", {"attempts": retry_attempt})
        else:
            logging.info(f"Sleeping {RETRY_TIMEOUT}s before next attempt.")
            await sleep(RETRY_TIMEOUT)
            await scrape_dental(
                pages=pages, proxy=proxy, retry_attempt=retry_attempt + 1
            )
