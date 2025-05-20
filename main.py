import feedparser
import pandas as pd
import sqlite3
import time
import logging
import requests
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, redirect
from langdetect import detect
from textblob import TextBlob
import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Updated RSS feeds for 25 countries (replaced problematic feeds)
RSS_FEEDS = {
    'UK': {'agency': 'BBC', 'url': 'http://feeds.bbci.co.uk/news/rss.xml', 'archive': 'https://www.bbc.com/news'},
    'USA': {'agency': 'CNN', 'url': 'http://rss.cnn.com/rss/edition.rss'},
    'Qatar': {'agency': 'Al Jazeera', 'url': 'https://www.aljazeera.com/xml/rss/all.xml', 'archive': 'https://www.aljazeera.com/news'},
    'Japan': {'agency': 'NHK', 'url': 'https://www3.nhk.or.jp/nhkworld/en/news/rss.xml'},
    'India': {'agency': 'The Times of India', 'url': 'https://timesofindia.indiatimes.com/rssfeedstopstories.cms'},
    'Singapore': {'agency': 'CNA', 'url': 'https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml'},
    'Malaysia': {'agency': 'New Straits Times', 'url': 'https://www.nst.com.my/feed'},
    'Indonesia': {'agency': 'Jakarta Globe', 'url': 'https://jakartaglobe.id/contexts/indonesia/rss'},
    'South Korea': {'agency': 'Korea Herald', 'url': 'http://www.koreaherald.com/rss'},
    'China': {'agency': 'Xinhua', 'url': 'http://www.xinhuanet.com/english/rss/worldrss.xml'},
    'Australia': {'agency': 'ABC News', 'url': 'https://www.abc.net.au/news/feed/51120/rss.xml'},
    'Germany': {'agency': 'DW', 'url': 'https://rss.dw.com/xml/rss_en_top'},
    'France': {'agency': 'France 24', 'url': 'https://www.france24.com/en/rss'},
    'Brazil': {'agency': 'Globo', 'url': 'https://g1.globo.com/rss/g1/brasil/'},
    'South Africa': {'agency': 'News24', 'url': 'https://feeds.news24.com/articles/news24/TopStories/rss'},
    'Canada': {'agency': 'CBC', 'url': 'https://www.cbc.ca/cmlink/rss-canada'},
    'Russia': {'agency': 'TASS', 'url': 'https://tass.com/rss/v2.xml'},
    'Mexico': {'agency': 'Reforma', 'url': 'https://www.reforma.com/rss/portada.xml'},
    'Nigeria': {'agency': 'Punch', 'url': 'https://punchng.com/feed/'},
    'Egypt': {'agency': 'Daily News Egypt', 'url': 'https://dailynewsegypt.com/feed/'},
    'Argentina': {'agency': 'La Nacion', 'url': 'https://www.lanacion.com.ar/arc/outboundfeeds/rss/?outputType=xml'},
    'Italy': {'agency': 'ANSA', 'url': 'https://www.ansa.it/english/rss.xml'},
    'Spain': {'agency': 'El Mundo', 'url': 'https://e00-elmundo.uecdn.es/elmundo/rss/portada.xml'},
    'Turkey': {'agency': 'Hurriyet', 'url': 'https://www.hurriyetdailynews.com/rss'},
    'Kenya': {'agency': 'Standard Media', 'url': 'https://www.standardmedia.co.ke/rss'},
}

NEWSAPI_KEY = '4b0f11755c7b49a396691e29fd45f586'

class NewsScraper:
    def __init__(self):
        self.data = []
        self.conn = sqlite3.connect('news_data.db')
        self.create_table()

    def create_table(self):
        """Create SQLite table to store news data."""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                pub_date TEXT,
                source TEXT,
                country TEXT,
                summary TEXT,
                url TEXT UNIQUE,
                language TEXT,
                sentiment TEXT
            )
        ''')
        self.conn.commit()

    def clean_text(self, text):
        """Clean text by removing extra whitespace and handling encoding."""
        if not text:
            return ""
        text = re.sub(r'\s+', ' ', text).strip()
        return text.encode('utf-8', errors='ignore').decode('utf-8')

    def detect_language(self, text):
        """Detect language of the text."""
        try:
            return detect(text)
        except:
            return 'unknown'

    def analyze_sentiment(self, text):
        """Analyze sentiment of the text using TextBlob."""
        try:
            analysis = TextBlob(text)
            polarity = analysis.sentiment.polarity
            if polarity > 0:
                return 'positive'
            elif polarity < 0:
                return 'negative'
            else:
                return 'neutral'
        except:
            return 'unknown'

    def parse_rss_feed(self, country, agency, url):
        """Parse a single RSS feed."""
        logging.info(f"Parsing RSS feed for {country} - {agency}")
        try:
            feed = feedparser.parse(url)
            if feed.bozo:
                logging.warning(f"Error parsing feed for {agency}: {feed.bozo_exception}")
                return

            for entry in feed.entries:
                title = self.clean_text(entry.get('title', ''))
                summary = self.clean_text(entry.get('summary', entry.get('description', '')))
                url = entry.get('link', '')
                pub_date = entry.get('published', entry.get('updated', ''))

                try:
                    pub_date = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z').isoformat()
                except:
                    pub_date = datetime.now().isoformat()

                language = self.detect_language(title + ' ' + summary)
                sentiment = self.analyze_sentiment(title + ' ' + summary)

                self.data.append({
                    'title': title,
                    'pub_date': pub_date,
                    'source': agency,
                    'country': country,
                    'summary': summary,
                    'url': url,
                    'language': language,
                    'sentiment': sentiment
                })

        except Exception as e:
            logging.error(f"Failed to parse {agency} RSS feed: {e}")

    def scrape_archive(self, country, agency, archive_url):
        """Scrape archive page for historical data."""
        logging.info(f"Scraping archive for {country} - {agency}")
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(archive_url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            articles = soup.find_all('a', class_='gs-c-promo-heading') if 'bbc' in archive_url else soup.find_all('a')
            for article in articles[:10]:  # Limit to 10 articles
                title = self.clean_text(article.get_text())
                url = article.get('href', '')
                if not url.startswith('http'):
                    url = f"https://{'www.bbc.com' if 'bbc' in archive_url else 'www.aljazeera.com'}{url}"
                
                pub_date = (datetime.now() - timedelta(days=365)).isoformat()
                summary = title  # Placeholder
                language = self.detect_language(title)
                sentiment = self.analyze_sentiment(title)

                self.data.append({
                    'title': title,
                    'pub_date': pub_date,
                    'source': agency,
                    'country': country,
                    'summary': summary,
                    'url': url,
                    'language': language,
                    'sentiment': sentiment
                })

        except Exception as e:
            logging.error(f"Failed to scrape archive for {agency}: {e}")

    def fetch_newsapi(self, country, agency):
        """Fetch historical data from NewsAPI."""
        logging.info(f"Fetching NewsAPI data for {country} - {agency}")
        try:
            from_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            url = f'https://newsapi.org/v2/everything?q={agency}&from={from_date}&apiKey={NEWSAPI_KEY}'
            response = requests.get(url, timeout=10)
            articles = response.json().get('articles', [])

            for article in articles:
                title = self.clean_text(article.get('title', ''))
                summary = self.clean_text(article.get('description', ''))
                url = article.get('url', '')
                pub_date = article.get('publishedAt', datetime.now().isoformat())
                language = self.detect_language(title + ' ' + summary)
                sentiment = self.analyze_sentiment(title + ' ' + summary)

                self.data.append({
                    'title': title,
                    'pub_date': pub_date,
                    'source': agency,
                    'country': country,
                    'summary': summary,
                    'url': url,
                    'language': language,
                    'sentiment': sentiment
                })

        except Exception as e:
            logging.error(f"Failed to fetch NewsAPI for {agency}: {e}")

    def scrape_all(self):
        """Scrape RSS feeds, archives, and NewsAPI."""
        for country, feed in RSS_FEEDS.items():
            self.parse_rss_feed(country, feed['agency'], feed['url'])
            self.fetch_newsapi(country, feed['agency'])
            if 'archive' in feed:
                self.scrape_archive(country, feed['agency'], feed['archive'])
            time.sleep(1)  # Rate limiting

    def save_to_csv(self):
        """Save data to CSV."""
        if not self.data:
            logging.warning("No data to save to CSV")
            return
        df = pd.DataFrame(self.data)
        df.drop_duplicates(subset=['url'], inplace=True)
        df.to_csv('news_data.csv', index=False, encoding='utf-8')
        logging.info("Data saved to news_data.csv")

    def save_to_db(self):
        """Save data to SQLite."""
        if not self.data:
            logging.warning("No data to save to database")
            return
        cursor = self.conn.cursor()
        for item in self.data:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO news (title, pub_date, source, country, summary, url, language, sentiment)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item['title'],
                    item['pub_date'],
                    item['source'],
                    item['country'],
                    item['summary'],
                    item['url'],
                    item['language'],
                    item['sentiment']
                ))
            except sqlite3.IntegrityError:
                continue
        self.conn.commit()
        logging.info("Data saved to SQLite database")

    def close_db(self):
        """Close database connection."""
        self.conn.close()

# Flask API
app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    """Redirect root URL to API endpoint."""
    return redirect('/api/news')

@app.route('/api/news', methods=['GET'])
def get_news():
    """API endpoint to retrieve news with filters."""
    country = request.args.get('country')
    language = request.args.get('language')
    start_date = request.args.get('start_date')
    
    conn = sqlite3.connect('news_data.db')
    cursor = conn.cursor()
    query = "SELECT * FROM news WHERE 1=1"
    params = []

    if country:
        query += " AND country = ?"
        params.append(country)
    if language:
        query += " AND language = ?"
        params.append(language)
    if start_date:
        query += " AND pub_date >= ?"
        params.append(start_date)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    columns = ['id', 'title', 'pub_date', 'source', 'country', 'summary', 'url', 'language', 'sentiment']
    news_data = [dict(zip(columns, row)) for row in rows]
    return jsonify(news_data)

def main():
    """Main function."""
    scraper = NewsScraper()
    scraper.scrape_all()
    scraper.save_to_csv()
    scraper.save_to_db()
    scraper.close_db()
    logging.info("Scraping completed")

if __name__ == "__main__":
    main()
    # Uncomment to run Flask API
    app.run(debug=False)