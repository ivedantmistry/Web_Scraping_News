from flask import Flask, jsonify, request, redirect
import sqlite3
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
    
    try:
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
        logging.info(f"Returning {len(news_data)} articles from API")
        return jsonify(news_data)
    except Exception as e:
        logging.error(f"Error querying database: {e}")
        return jsonify({"error": "Failed to retrieve news data"}), 500

if __name__ == "__main__":
    logging.info("Starting Flask API server on http://localhost:5000/api/news")
    app.run(debug=False, host='0.0.0.0', port=5000)