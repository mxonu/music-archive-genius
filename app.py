"""
Веб-приложение Flask для просмотра и поиска музыкальных данных.

Запуск: python app.py
Сайт: http://127.0.0.1:5000
"""

import json
import os
from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

MUSIC_DATA_FILE = 'music_data.json'


def load_music_data():
    """Загружает данные из JSON-файла"""
    try:
        if os.path.exists(MUSIC_DATA_FILE):
            with open(MUSIC_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Ошибка при загрузке данных: {e}")
    return []


def search_in_data(data, query):
    """
    Ищет результаты в данных
    """
    if not query:
        return data
    
    query = query.lower().strip()
    filtered = []
    
    for artist in data:
        artist_match = query in artist['artist'].lower()
        
        filtered_songs = [
            song for song in artist['songs']
            if query in song['title'].lower() or 
               query in song['lyrics'].lower()
        ]
        
        if artist_match:
            filtered.append(artist)
        elif filtered_songs:
            filtered.append({
                "artist": artist['artist'],
                "country": artist.get('country', 'Unknown'),
                "genius_url": artist.get('genius_url', ''),
                "image_url": artist.get('image_url', ''),
                "songs": filtered_songs
            })
    
    return filtered


@app.route('/')
def index():
    """Главная страница"""
    music_data = load_music_data()
    search_query = request.args.get('search', '').strip()
    
    if search_query:
        displayed_data = search_in_data(music_data, search_query)
    else:
        displayed_data = music_data
    
    total_artists = len(music_data)
    total_songs = sum(len(artist['songs']) for artist in music_data)
    displayed_artists = len(displayed_data)
    displayed_songs = sum(len(artist['songs']) for artist in displayed_data)
    
    return render_template(
        'index.html',
        music_data=displayed_data,
        search_query=search_query,
        total_artists=total_artists,
        total_songs=total_songs,
        displayed_artists=displayed_artists,
        displayed_songs=displayed_songs
    )


@app.route('/artist/<artist_name>')
def artist_page(artist_name):
    """Страница артиста"""
    music_data = load_music_data()
    
    for artist in music_data:
        if artist['artist'].lower() == artist_name.lower():
            return render_template('artist.html', artist=artist)
    
    return render_template('404.html', message=f"Артист '{artist_name}' не найден"), 404


@app.route('/api/artists')
def api_artists():
    """API: Список всех артистов"""
    music_data = load_music_data()
    artists = [
        {
            "name": artist['artist'],
            "country": artist.get('country', 'Unknown'),
            "songs_count": len(artist['songs']),
            "url": f"/artist/{artist['artist']}"
        }
        for artist in music_data
    ]
    return jsonify(artists)


@app.route('/api/artist/<artist_name>')
def api_artist(artist_name):
    """API: Информация об артисте"""
    music_data = load_music_data()
    
    for artist in music_data:
        if artist['artist'].lower() == artist_name.lower():
            return jsonify(artist)
    
    return jsonify({"error": "Artist not found"}), 404


@app.route('/api/search')
def api_search():
    """API: Поиск"""
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400
    
    music_data = load_music_data()
    results = search_in_data(music_data, query)
    
    return jsonify(results)


@app.route('/api/stats')
def api_stats():
    """API: Статистика"""
    music_data = load_music_data()
    
    total_artists = len(music_data)
    total_songs = sum(len(artist['songs']) for artist in music_data)
    
    stats_by_country = {}
    for artist in music_data:
        country = artist.get('country', 'Unknown')
        stats_by_country[country] = stats_by_country.get(country, 0) + 1
    
    return jsonify({
        "total_artists": total_artists,
        "total_songs": total_songs,
        "artists_by_country": stats_by_country,
        "last_updated": datetime.now().isoformat()
    })


@app.errorhandler(404)
def page_not_found(error):
    """404 ошибка"""
    return render_template('404.html'), 404


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🎵 МУЗЫКАЛЬНЫЙ АРХИВ")
    print("="*60)
    print("\n📱 http://127.0.0.1:5000")
    print("Нажмите Ctrl+C для остановки\n")
    
    app.run(debug=True, host='127.0.0.1', port=5000)
