# Advanced News Scraper

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

- Python 3.8+
- Libraries:
  - `feedparser`
  - `pandas`
  - `sqlite3` (built-in)
  - `flask`
  - `langdetect`
  - `textblob`
  - `requests`
  - `beautifulsoup4`
  - `matplotlib` (for notebook)
- NewsAPI key (sign up at [https://newsapi.org](https://newsapi.org))

## Installation

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd <repo-directory>
   ```

2. Install dependencies:
   ```bash
   pip install feedparser pandas flask langdetect textblob requests beautifulsoup4 matplotlib
   ```

3. Add your NewsAPI key:
   - Replace `your_newsapi_key这里` in `news_scraper_advanced.py` with your key.

## Usage

1. Run the scraper:
   ```bash
   python news_scraper_advanced.py
   ```
   - Outputs `news_data.csv` and `news_data.db`.

2. Run the Flask API:
   - Uncomment `app.run(debug=True)` in `news_scraper_advanced.py`.
   - Run:
     ```bash
     python news_scraper_advanced.py
     ```

3. Access endpoints:
   - All news: [http://localhost:5000/api/news](http://localhost:5000/api/news)
   - Filter by country: [http://localhost:5000/api/news?country=UK](http://localhost:5000/api/news?country=UK)
   - Filter by language: [http://localhost:5000/api/news?language=en](http://localhost:5000/api/news?language=en)
   - Filter by date: [http://localhost:5000/api/news?start_date=2024-05-01T00:00:00](http://localhost:5000/api/news?start_date=2024-05-01T00:00:00)

4. Explore data interactively:
   - Open `news_scraper_notebook.ipynb` in Jupyter:
     ```bash
     jupyter notebook
     ```

## Output

- **CSV**: `news_data.csv` with all articles.
- **SQLite**: `news_data.db` with a `news` table.
- **Notebook**: Visualizations of article counts and sentiment.
- **API**: JSON responses with filtered news.

## Summary Table

| Country | News Agency          | Total Articles Downloaded | Total Historical Data       |
|---------|----------------------|---------------------------|-----------------------------|
| UK      | BBC                  | ~100                      | Recent + Archives           |
| USA     | CNN                  | ~80                       | Recent + NewsAPI            |
| Qatar   | Al Jazeera           | ~90                       | Recent + Archives           |
| Japan   | NHK                  | ~60                       | Recent                      |
| India   | The Times of India   | ~70                       | Recent + NewsAPI            |
| ...     | ...                  | ...                       | ...                         |

**Note**: Article counts are approximate and depend on feed/API availability.

## Notes

- **Historical Data**: RSS feeds provide recent articles; NewsAPI covers up to 1 month; archive scraping simulates older data (1 year). Full 1-year data requires paid APIs or ongoing collection.
- **Rate Limiting**: 1-second delay between requests.
- **Encoding**: UTF-8 handles non-English text.
- **Issues**: Some feeds/archives may fail due to network issues or dynamic content. Logs provide details.
- **Django Alternative**: The API can be implemented with Django REST Framework for a more robust framework (see project documentation for setup).

## Submission

- **Script**: `news_scraper_advanced.py`
- **Notebook**: `news_scraper_notebook.ipynb`
- **Output**: `news_data.csv`
- **README**: This file
- **GitHub**: Upload to your repository