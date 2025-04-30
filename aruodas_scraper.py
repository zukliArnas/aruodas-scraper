import os
import time
import argparse

from playwright.sync_api import sync_playwright

from logger_config import get_logger
from utils import *
from locators import CITY_LOCATORS

logger = get_logger("info.log")

BASE_URL = "https://www.aruodas.lt"
START_URL = f"{BASE_URL}/butai/vilniuje/"


def parse_args():
    parser = argparse.ArgumentParser(description="Aruodas.lt Flat Information Scraper Scraper")
    parser.add_argument("--city", type=str, default="Vilnius", help="City to scrape flats from")
    return parser.parse_args()


def main():
    args = parse_args()

    logger.info("✅ Script started.")
    print("✅ Script started.")

    if args.city not in CITY_LOCATORS:
        logger.error(
            f"Sorry, this city - '{args.city}' is not supported, yet. Please pick only Vilnius, Kaunas or Klaipeda."
        )
        return

    city_selector = CITY_LOCATORS[args.city]
    all_flats = []

    with sync_playwright() as p:
        headless_mode = os.getenv("HEADLESS", "true").lower() == "true"
        browser = p.chromium.launch(headless=headless_mode)
        page = browser.new_page()
        page.goto(START_URL)
        time.sleep(2)

        accept_cookies(page)

        logger.info(f"Applying city filter: {args.city}")
        page.wait_for_selector("[id='display_FRegion']", timeout=10000)
        page.click("[id='display_FRegion']")
        page.click(city_selector)

        print("And I am so sorry, you cannot pick other filters yet :(")
        page.click('[id="buttonSearchForm"]')
        time.sleep(3)

        total_pages = get_total_pages(page)
        logger.info(f"Total pages found: {total_pages}")

        for i in range(1, 2): # only one page this time
            try:
                flats = scrape_page(page, i, START_URL) # only one page this time
                logger.info(f"Scraping page {i}")
                all_flats.extend(flats)
                time.sleep(1.5)
            except Exception as e:
                print(f"Error scraping page {i}: {e}")
                continue

        browser.close()

    flats_data = []

    for flat_url in all_flats:
        logger.info(f"Scraping flat: {flat_url}")
        flat_info = scrape_flat_page(flat_url)
        if flat_info:
            flats_data.append(flat_info)
            save_if_new(flat_info)

    
    logger.info(f"Total flats scraped: {len(flats_data)}")


if __name__ == "__main__":
    start_time = time.time()
    main()
    total_time = time.time() - start_time
    logger.info(f"Finished in {round(total_time, 2)} seconds")


