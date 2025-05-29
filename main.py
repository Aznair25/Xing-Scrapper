from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
from datetime import datetime
import pandas as pd
import requests
import time
import os
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI()

class ScrapeRequest(BaseModel):
    url: str


def click_cookie_button(driver):
    script = """
    const shadowHost = document.querySelector('#usercentrics-root');
    if (!shadowHost || !shadowHost.shadowRoot) return false;
    const acceptBtn = shadowHost.shadowRoot.querySelector('button[data-testid="uc-accept-all-button"]');
    if (acceptBtn) {
        acceptBtn.click();
        return true;
    }
    return false;
    """
    return driver.execute_script(script)

def translate_in_chunks(text, chunk_size=4900):
    translated_text = ""
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size]
        translated_chunk = GoogleTranslator(source='auto', target='en').translate(chunk)
        translated_text += translated_chunk + " "
    return translated_text.strip()

def scrape_new_jobs(driver, seen_links, job_list, job_file):
    html_cont = driver.page_source
    soup = BeautifulSoup(html_cont, 'lxml')
    containers = soup.find_all('a', class_='job-teaser-list-item-styles__Link-sc-4c7b5190-0 xIBsy result__Item-sc-2a2728af-0 lmsxAA')

    new_jobs = 0

    for con in containers:
        try:
            link = con['href']
            if not link.startswith('/jobs/') or ("https://www.xing.com" + link) in seen_links:
                continue

            full_url = "https://www.xing.com" + link
            seen_links.add(full_url)
            logger.info(f"Processing job: {full_url}")

            position_0 = con.find('h2').text
            position = GoogleTranslator(source='auto', target='en').translate(position_0)

            city = con.find('p', class_='job-teaser-list-item-styles__City-sc-4c7b5190-6').text
            company = con.find('p', class_='job-teaser-list-item-styles__Company-sc-4c7b5190-7').text
            date_0 = con.find('p', class_='job-teaser-list-item-styles__Date-sc-4c7b5190-9').text
            date = GoogleTranslator(source='auto', target='en').translate(date_0)

            jd_html = requests.get(full_url).text
            jd_soup = BeautifulSoup(jd_html, 'lxml')
            jd_element = jd_soup.find('div', class_='description-module__BlurWrapper-sc-4a74f755-2 CJPS')
            jd = translate_in_chunks(jd_element.text) if jd_element else "N/A"

            job_list.append({
                'Job Title': position,
                'City': city,
                'Company Name': company,
                'Posting Time': date,
                'Link': full_url,
                'Job Description': jd,
                'Scrapped at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })

            new_jobs += 1

        except Exception as e:
            logger.error(f"Error processing job: {e}")

    if new_jobs > 0:
        pd.DataFrame(job_list).to_excel(job_file, index=False)
        logger.info(f"Saved {new_jobs} new jobs.")
    else:
        logger.info("No new jobs in this round.")

def start_scraping_session(url, job_file="Jobs.xlsx"):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument("window-size=1920,1080")
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    wait = WebDriverWait(driver, 15)

    try:
        wait.until(lambda d: click_cookie_button(d))
        logger.info("✅ Accepted cookies.")
    except Exception as e:
        logger.warning(f"❌ Could not accept cookies: {e}")

    seen_links = set()
    job_list = []
    if os.path.exists(job_file):
        df_existing = pd.read_excel(job_file)
        seen_links = set(df_existing['Link'].tolist())
        job_list = df_existing.to_dict('records')
        logger.info("📁 Loaded existing job records.")

    while True:
        scrape_new_jobs(driver, seen_links, job_list, job_file)
        try:
            show_more_button = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[.//span[contains(text(), 'Show more')]]")
            ))
            logger.info("🔁 Clicking 'Show more' button...")
            driver.execute_script("arguments[0].scrollIntoView(true);", show_more_button)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", show_more_button)
            time.sleep(2)
        except Exception:
            logger.info("✅ No more jobs to load or 'Show more' button not clickable.")
            break

    driver.quit()
    logger.info("🎉 Scraping session completed.")


@app.post("/scrape_jobs")
def scrape_jobs(request: ScrapeRequest):
    try:
        logger.info(f"📡 Received scraping request for URL: {request.url}")
        start_scraping_session(request.url)
        return {"status": "success", "message": "Scraping completed successfully."}
    except Exception as e:
        logger.error(f"Unhandled error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
