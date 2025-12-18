import json
import os
from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

DATA_FILE = 'music_data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            f = open(DATA_FILE, 'r', encoding='utf-8')
            data = json.load(f)
            f.close()
            return data
        except:
            print("Ошибка чтения файла")
            return []
    else:
        return []

def search_data(data, query):
    if query == '':
        return data
    
    query = query.lower()
    results = []
    
    for artist in data:
        if query in artist['artist'].lower():
            results.append(artist)
            continue
        
        found_songs = []
        for song in artist['songs']:
            if query in song['title'].lower():
                found_songs.append(song)
            elif query in song['lyrics'].lower():
                found_songs.append(song)
        
        if len(found_songs) > 0:
            results.append({
                "artist": artist['artist'],
                "genius_url": artist.get('genius_url', ''),
                "image_url": artist.get('image_url', ''),
                "songs": found_songs
            })
    
    return results

@app.route('/')
def index():
    data = load_data()
    search = request.args.get('search', '').strip()
    
    if search:
        displayed = search_data(data, search)
    else:
        displayed = data
    
    total_artists = len(data)
    total_songs = 0
    for artist in data:
        total_songs += len(artist['songs'])
    
    shown_artists = len(displayed)
    shown_songs = 0
    for artist in displayed:
        shown_songs += len(artist['songs'])
    
    return render_template(
        'index.html',
        music_data=displayed,
        search_query=search,
        total_artists=total_artists,
        total_songs=total_songs,
        displayed_artists=shown_artists,
        displayed_songs=shown_songs
    )

@app.route('/artist/<artist_name>')
def artist_page(artist_name):
    data = load_data()
    
    found = None
    for artist in data:
        if artist['artist'].lower() == artist_name.lower():
            found = artist
            break
    
    if found:
        return render_template('artist.html', artist=found)
    else:
        return render_template('404.html', message=f"Артист '{artist_name}' не найден"), 404

@app.route('/api/artists')
def api_artists():
    data = load_data()
    
    result = []
    for artist in data:
        result.append({
            "name": artist['artist'],
            "country": artist.get('country', 'Unknown'),
            "songs_count": len(artist['songs']),
            "url": f"/artist/{artist['artist']}"
        })
    
    return jsonify(result)

@app.route('/api/artist/<artist_name>')
def api_artist(artist_name):
    data = load_data()
    
    for artist in data:
        if artist['artist'].lower() == artist_name.lower():
            return jsonify(artist)
    
    return jsonify({"error": "Artist not found"}), 404

@app.route('/api/search')
def api_search():
    q = request.args.get('q', '').strip()
    
    if q == '':
        return jsonify({"error": "Query is empty"}), 400
    
    data = load_data()
    results = search_data(data, q)
    
    return jsonify(results)

@app.route('/api/stats')
def api_stats():
    data = load_data()
    
    total_artists = len(data)
    total_songs = 0
    for artist in data:
        total_songs += len(artist['songs'])
    
    countries = {}
    for artist in data:
        country = artist.get('country', 'Unknown')
        if country in countries:
            countries[country] += 1
        else:
            countries[country] = 1
    
    return jsonify({
        "total_artists": total_artists,
        "total_songs": total_songs,
        "artists_by_country": countries,
        "last_updated": datetime.now().isoformat()
    })

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    print("\n" + "="*50)
    print("МУЗЫКАЛЬНЫЙ АРХИВ")
    print("="*50)
    print("\nСервер: http://127.0.0.1:5000")
    print("Остановить сервер: Ctrl+C\n")
    
    app.run(debug=True, host='127.0.0.1', port=5000)
