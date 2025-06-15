import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from .cookies import click_cookie_button
from .translator import translate_in_chunks
from bs4 import BeautifulSoup
import requests
from .logger import logger

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
            position =translate_in_chunks(position_0) if position_0 else "N/A"

            city = con.find('p', class_='job-teaser-list-item-styles__City-sc-4c7b5190-6').text
            company = con.find('p', class_='job-teaser-list-item-styles__Company-sc-4c7b5190-7').text
            date_0 = con.find('p', class_='job-teaser-list-item-styles__Date-sc-4c7b5190-9').text
            date = translate_in_chunks(date_0) if date_0 else "N/A"

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

def start_scraping_session(url, job_file="data/jobs.xlsx"):
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

    seen_links, job_list = set(), []
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