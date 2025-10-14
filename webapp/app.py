"""Flask web application for streaming anime episodes."""
import json
import os
from flask import Flask, render_template, request, jsonify
from scraper.database import Database, DatabaseConfig

app = Flask(__name__)

def get_db():
    """Get database connection."""
    db = Database()
    db.connect()
    return db

@app.route('/')
def index():
    """Home page with search."""
    return render_template('index.html')

@app.route('/search')
def search():
    """Search for series."""
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    db = get_db()
    cursor = db._connection.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT id, name, image_url, genres, categories, languages
            FROM series 
            WHERE name LIKE %s
            ORDER BY name
            LIMIT 50
        """, (f'%{query}%',))
        
        results = cursor.fetchall()
        
        # Parse JSON fields
        for result in results:
            result['genres'] = json.loads(result['genres']) if result['genres'] else []
            result['categories'] = json.loads(result['categories']) if result['categories'] else []
            result['languages'] = json.loads(result['languages']) if result['languages'] else []
        
        return jsonify(results)
    finally:
        cursor.close()
        db.close()

@app.route('/series/<int:series_id>')
def series_detail(series_id):
    """Series detail page showing seasons."""
    db = get_db()
    cursor = db._connection.cursor(dictionary=True)
    
    try:
        # Get series info
        cursor.execute("""
            SELECT id, name, image_url, genres, categories, languages, 
                   synopsis, advancement, correspondence, is_mature
            FROM series 
            WHERE id = %s
        """, (series_id,))
        
        series = cursor.fetchone()
        if not series:
            return "Series not found", 404
        
        # Parse JSON fields
        series['genres'] = json.loads(series['genres']) if series['genres'] else []
        series['categories'] = json.loads(series['categories']) if series['categories'] else []
        series['languages'] = json.loads(series['languages']) if series['languages'] else []
        
        # Get seasons
        cursor.execute("""
            SELECT id, name, url
            FROM seasons 
            WHERE serie_id = %s
            ORDER BY id
        """, (series_id,))
        
        seasons = cursor.fetchall()
        
        return render_template('series.html', series=series, seasons=seasons)
    finally:
        cursor.close()
        db.close()

@app.route('/season/<int:season_id>')
def season_detail(season_id):
    """Season detail page showing episodes."""
    db = get_db()
    cursor = db._connection.cursor(dictionary=True)
    
    try:
        # Get season and series info
        cursor.execute("""
            SELECT s.id, s.name, s.url, se.id as serie_id, se.name as serie_name, se.image_url
            FROM seasons s
            JOIN series se ON s.serie_id = se.id
            WHERE s.id = %s
        """, (season_id,))
        
        season = cursor.fetchone()
        if not season:
            return "Season not found", 404
        
        # Get episodes
        cursor.execute("""
            SELECT id, episode_name, episode_index
            FROM episodes 
            WHERE season_id = %s
            ORDER BY episode_index
        """, (season_id,))
        
        episodes = cursor.fetchall()
        
        # Get available languages for this season
        cursor.execute("""
            SELECT DISTINCT p.language
            FROM players p
            JOIN episodes e ON p.episode_id = e.id
            WHERE e.season_id = %s
            ORDER BY p.language
        """, (season_id,))
        
        languages = [row['language'] for row in cursor.fetchall()]
        
        return render_template('season.html', season=season, episodes=episodes, languages=languages)
    finally:
        cursor.close()
        db.close()

@app.route('/episode/<int:episode_id>')
def episode_detail(episode_id):
    """Episode detail page with player."""
    db = get_db()
    cursor = db._connection.cursor(dictionary=True)
    
    try:
        # Get episode info
        cursor.execute("""
            SELECT e.id, e.episode_name, e.episode_index, e.serie_name, e.season_name,
                   s.id as season_id, se.id as serie_id, se.image_url
            FROM episodes e
            JOIN seasons s ON e.season_id = s.id
            JOIN series se ON s.serie_id = se.id
            WHERE e.id = %s
        """, (episode_id,))
        
        episode = cursor.fetchone()
        if not episode:
            return "Episode not found", 404
        
        # Get players grouped by language
        cursor.execute("""
            SELECT language, player_url, player_hostname, player_order
            FROM players 
            WHERE episode_id = %s
            ORDER BY language, player_order
        """, (episode_id,))
        
        players_data = cursor.fetchall()
        
        # Group players by language
        players = {}
        for player in players_data:
            lang = player['language']
            if lang not in players:
                players[lang] = []
            players[lang].append({
                'url': player['player_url'],
                'hostname': player['player_hostname'],
                'order': player['player_order']
            })
        
        return render_template('episode.html', episode=episode, players=players)
    finally:
        cursor.close()
        db.close()

@app.route('/api/series')
def api_series_list():
    """API endpoint to list all series."""
    db = get_db()
    cursor = db._connection.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT id, name, image_url, genres, categories
            FROM series 
            ORDER BY name
            LIMIT 100
        """)
        
        results = cursor.fetchall()
        
        # Parse JSON fields
        for result in results:
            result['genres'] = json.loads(result['genres']) if result['genres'] else []
            result['categories'] = json.loads(result['categories']) if result['categories'] else []
        
        return jsonify(results)
    finally:
        cursor.close()
        db.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
