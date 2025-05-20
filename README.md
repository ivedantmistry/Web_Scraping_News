# News Scraper

This project scrapes news from 25 countries using RSS feeds, NewsAPI, and archive scraping, storing data in CSV and SQLite. It includes a Flask API with filtering, language detection, sentiment analysis, and a Jupyter Notebook for interactive analysis.

## Features

- Scrapes news from 25 countries (e.g., BBC, CNN, Al Jazeera, The Times of India).
- Extracts: Title, Publication Date, Source, Country, Summary, URL, Language, Sentiment.
- Sources:
  - RSS feeds for recent articles.
  - NewsAPI for historical data (up to 1 month, free-tier limit).
  - Archive scraping for select outlets (e.g., BBC, Al Jazeera).
- Stores data in CSV (`news_data.csv`) and SQLite (`news_data.db`).
- Handles UTF-8 encoding and removes duplicates.
- Flask API with filtering by country, language, and date.
- Language detection using `langdetect`.
- Sentiment analysis using `textblob`.
- Jupyter Notebook (`news_scraper_notebook.ipynb`) with visualizations.

## Requirements

- Python 3.12
- Libraries:
  - `feedparser`
  - `pandas`
  - `sqlite3`
  - `flask`
  - `langdetect`
  - `textblob`
  - `requests`
  - `beautifulsoup4`
- NewsAPI key ([https://newsapi.org](https://newsapi.org))

## Usage

1. Run the scraper:
   ```bash
   python main.py
   ```
   - Outputs `news_data.csv` and `news_data.db`.

2.  Access endpoints:
   - All news: [http://localhost:5000/api/news](http://localhost:5000/api/news)
   - Filter by country: [http://localhost:5000/api/news?country=UK](http://localhost:5000/api/news?country=UK)
   - Filter by language: [http://localhost:5000/api/news?language=en](http://localhost:5000/api/news?language=en)
   - Filter by date: [http://localhost:5000/api/news?start_date=2024-05-01T00:00:00](http://localhost:5000/api/news?start_date=2024-05-01T00:00:00)

## Output

- **CSV**: `news_data.csv` with all articles.
- **SQLite**: `news_data.db` with a `news` table.
- **API**: JSON responses with filtered news.
