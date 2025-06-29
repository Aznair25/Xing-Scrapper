# 📌 Xing Scrapper

**Xing Scrapper** is a powerful web scraper built with FastAPI, Selenium, BeautifulSoup, and deep-translator. It automates fetching and translating job listings from **Xing**, the leading job platform in German-speaking countries—Germany, Austria, and Switzerland.

Since most job postings on Xing are in German, this tool integrates GoogleTranslator to convert titles, descriptions, and dates into English, making job data globally accessible.

---

## 🚀 Features

* **FastAPI endpoint** (`/scrape_jobs`) to start scraping remotely.
* **Selenium automation**: accepts cookies, loads dynamic job listings, and clicks "Show more" until completion.
* **BeautifulSoup parsing** for efficient extraction of job teasers.
* **Chunked translation** with GoogleTranslator—handles long German text without hitting limits.
* **Excel persistence** (`data/jobs.xlsx`): avoids duplicates, appends new entries with timestamps.
* **Structured logging** provides clear traceability and error handling.

---

## 📂 Project Structure

```
Xing_Scrapper/
├── app/
│   ├── main.py           # FastAPI app with /scrape_jobs endpoint
│   ├── scraper.py        # Core scraping & translation logic
│   ├── cookies.py        # Cookie acceptance via JavaScript
│   ├── translator.py     # Chunked translation logic
│   ├── models.py         # Pydantic request schema
│   └── logger.py         # Logging configuration
├── data/
│   └── jobs.xlsx         # Output Excel (auto-generated)
├── requirements.txt      # Project dependencies
├── .gitignore
└── README.md
```

---

## 🛠️ Installation

1. **Clone** this repo:

   ```bash
   git clone https://github.com/Aznair25/Xing-Scrapper.git
   cd Xing_Scrapper
   ```

2. **Install dependencies**:

   ```
   pip install -r requirements.txt
   ```

3. **Run the app**:

   ```
   uvicorn app.main:app --reload
   ```

---

## 🔧 Usage

Trigger scraping by sending a POST request:

```bash
curl -X POST "http://localhost:8000/scrape_jobs" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://www.xing.com/jobs"}'
```

This launches a headless Chrome session that:

* Accepts cookies
* Loads all job listings via “Show more”
* Extracts German job posts
* Translates and saves them to `data/jobs.xlsx`

---

## 🌐 Why Xing?

* **Extensively used** in the DACH region: 22 million registered users and over 1 million job listings.
* **Strong regional reach** with 20,000+ recruiters actively posting jobs.
* **Focused on German-language jobs**, making translation essential for global understanding.

---

## 💼 Future Roadmap

This project will soon be extended to automatically **apply to jobs**. It will simulate submitting applications on supported platforms—allowing seamless end-to-end automation from scraping to applying.

---

## ✅ Requirements

Dependencies listed in `requirements.txt`:

```
lxml
openpyxl
deep_translator
selenium
requests
pandas
bs4
fastapi
uvicorn
```

---

## 📈 Showcase of Scraping Skills

* **Dynamic content handling**: accepts cookies, scrolls pages, and clicks "Show more".
* **Chunked translation**: avoids API limits when translating large texts.
* **Deduplication with persistence**: keeps track of seen job links via Excel.
* **Modular and testable architecture**: clean separation of core features.
* **API-ready**: integrates with workflows via FastAPI endpoint.

---

## 👋 Feedback & Contributions

Have ideas or improvements? Submit an issue or PR—contributions are welcome!

---

**Xing Scrapper** turns German job listings into polished English datasets and aims to evolve into an automated job applicant—showcasing full-stack scraping, translation, and automation proficiency.