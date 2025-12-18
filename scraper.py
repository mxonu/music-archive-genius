import json
import os
import time
from dotenv import load_dotenv
import lyricsgenius

load_dotenv()

token = os.getenv('GENIUS_TOKEN')
if not token:
    print("Ошибка: токен не найден!")
    print("Создай .env файл и добавь GENIUS_TOKEN=твой_токен")
    exit()

genius = lyricsgenius.Genius(token, skip_non_songs=True, excluded_terms=["Remix", "Cover"])
genius.verbose = False

def load_json():
    filename = 'music_data.json'
    
    if os.path.exists(filename):
        try:
            f = open(filename, 'r', encoding='utf-8')
            data = json.load(f)
            f.close()
            print(f"Загружено: {len(data)} артистов")
            return data
        except:
            print("Ошибка чтения, создаю новый файл")
            return []
    else:
        print("Файл не найден, создаю новый")
        return []

def save_json(data):
    filename = 'music_data.json'
    
    try:
        f = open(filename, 'w', encoding='utf-8')
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.close()
        print("Сохранено в", filename)
    except Exception as e:
        print("Ошибка:", e)

def check_artist(data, name):
    for artist in data:
        if artist['artist'].lower() == name.lower():
            return True
    return False

def parse_artist(name, songs_count=5):
    print(f"\n>>> Ищу: {name}")
    
    try:
        artist = genius.search_artist(name, max_songs=songs_count)
        
        if artist == None:
            print("Не найден")
            return None
        
        print(f"Найден: {artist.name}")
        
        result = {
            "artist": artist.name,
            "genius_url": artist.url,
            "image_url": None,
            "songs": []
        }
        
        if hasattr(artist, 'image_url'):
            result['image_url'] = artist.image_url
        
        print("Собираю песни...")
        count = 0
        
        for song in artist.songs:
            if count >= songs_count:
                break
            
            try:
                text = "Текст недоступен"
                if hasattr(song, 'lyrics') and song.lyrics:
                    text = song.lyrics
                
                song_info = {
                    "title": song.title,
                    "year": None,
                    "lyrics": text,
                    "genius_url": None,
                    "featured_artists": []
                }
                
                if hasattr(song, 'year'):
                    song_info['year'] = song.year
                
                if hasattr(song, 'url'):
                    song_info['genius_url'] = song.url
                
                if hasattr(song, 'featured_artists'):
                    song_info['featured_artists'] = song.featured_artists
                
                result['songs'].append(song_info)
                count += 1
                print(f"  [{count}] {song.title}")
                
                time.sleep(0.3)  
                
            except Exception as e:
                print(f"  Ошибка с песней: {e}")
                continue
        
        if len(result['songs']) == 0:
            print("Песни не найдены")
            return None
        
        print(f"Готово! Добавлено песен: {len(result['songs'])}")
        return result
        
    except Exception as e:
        print(f"Ошибка парсинга: {e}")
        return None

def parse_list(names, songs=5):
    database = load_json()
    
    print("\n" + "="*50)
    print(f"Начинаю парсинг ({len(names)} артистов)")
    print("="*50)
    
    new_count = 0
    
    for name in names:
        if check_artist(database, name):
            print(f"\n>>> Пропускаю: {name} (уже есть)")
            continue
        
        artist_data = parse_artist(name, songs)
        
        if artist_data:
            database.append(artist_data)
            new_count += 1
        
        time.sleep(1.5)  
    
    save_json(database)
    
    total_songs = 0
    for artist in database:
        total_songs += len(artist['songs'])
    
    print("\n" + "="*50)
    print("ИТОГО:")
    print(f"  Артистов в базе: {len(database)}")
    print(f"  Добавлено новых: {new_count}")
    print(f"  Всего песен: {total_songs}")
    print("="*50 + "\n")

def manual_input():
    print("\n" + "="*50)
    print("РУЧНОЙ ВВОД")
    print("="*50)
    print("Вводи имена артистов (для выхода: exit)")
    
    artists = []
    
    while True:
        name = input("\nАртист: ").strip()
        
        if name.lower() == 'exit' or name == '':
            break
        
        artists.append(name)
        print(f"  OK: {name}")
    
    if len(artists) > 0:
        songs = input("\nСколько песен на артиста? [5]: ").strip()
        
        if songs == '':
            songs = 5
        else:
            songs = int(songs)
        
        parse_list(artists, songs)
    else:
        print("Ничего не введено")

def show_database():
    data = load_json()
    
    if len(data) == 0:
        print("\nБаза пуста")
        return
    
    print("\n" + "="*50)
    print("БАЗА ДАННЫХ")
    print("="*50)
    
    total = 0
    for artist in data:
        songs_count = len(artist['songs'])
        total += songs_count
        print(f"\n{artist['artist']} ({songs_count} песен)")
        
        for i, song in enumerate(artist['songs'][:3]):
            print(f"  {i+1}. {song['title']}")
        
        if songs_count > 3:
            print(f"  ... и ещё {songs_count - 3}")
    
    print(f"\nВсего: {len(data)} артистов, {total} песен")
    print("="*50 + "\n")


def main():
    print("\n" + "="*50)
    print("GENIUS PARSER v1.0")
    print("Парсер музыки с Genius.com")
    print("="*50)
    
    print("\nВыбери режим:")
    print("[1] Ручной ввод")
    print("[2] Автоматический (популярные артисты)")
    print("[3] Показать базу")
    print("[0] Выход")
    
    choice = input("\n>>> ").strip()
    
    if choice == '1':
        manual_input()
    
    elif choice == '2':
        artists = [
            # Поп и R&B
            "The Weeknd", "Taylor Swift", "Ariana Grande", "Billie Eilish",
            "Ed Sheeran", "Justin Bieber", "Rihanna", "Drake", "Post Malone",
            "Dua Lipa", "Lady Gaga", "Adele", "Beyoncé", "Katy Perry",
            "Bruno Mars", "Shawn Mendes", "Selena Gomez", "Sia", "Charlie Puth",
            
            # Рок и Альтернатива
            "Imagine Dragons", "Twenty One Pilots", "Coldplay", "Linkin Park",
            "Arctic Monkeys", "The Killers", "Muse", "Green Day", "Red Hot Chili Peppers",
            "Foo Fighters", "Panic! at the Disco", "Fall Out Boy", "Paramore",
            "Nirvana", "Queen", "The Beatles", "Pink Floyd", "Led Zeppelin",
            
            # Хип-хоп и Рэп
            "Eminem", "Kendrick Lamar", "J. Cole", "Travis Scott", "Kanye West",
            "Lil Wayne", "Nicki Minaj", "Cardi B", "21 Savage", "Future",
            "Migos", "Lil Uzi Vert", "Juice WRLD", "XXXTentacion", "Tyler, The Creator",
            
            # Электронная музыка
            "Calvin Harris", "The Chainsmokers", "Avicii", "David Guetta",
            "Marshmello", "Kygo", "Zedd", "Alan Walker", "Martin Garrix",
            
            # Кантри
            "Luke Combs", "Morgan Wallen", "Chris Stapleton", "Thomas Rhett",
            "Kane Brown", "Carrie Underwood",
            
            # Латиноамериканская музыка
            "Bad Bunny", "J Balvin", "Daddy Yankee", "Ozuna", "Maluma",
            "Rosalía", "Shakira", "Enrique Iglesias",
            
            # Инди и Альтернатива
            "Tame Impala", "Glass Animals", "Foster the People", "MGMT",
            "The Strokes", "Vampire Weekend", "Florence + The Machine",
            
            # Классика и легенды
            "Michael Jackson", "Madonna", "Prince", "David Bowie", "Elton John",
            "Bob Dylan", "The Rolling Stones", "AC/DC", "Metallica",
            
            # Современный рок
            "Greta Van Fleet", "Royal Blood", "Nothing But Thieves",
            "Bring Me The Horizon", "My Chemical Romance"
        ]
        
        songs = input("Сколько песен на артиста? [3]: ").strip()
        songs = int(songs) if songs else 3
        
        parse_list(artists, songs)
    
    elif choice == '3':
        show_database()
    
    elif choice == '0':
        print("Выход")
    
    else:
        print("Неверный выбор!")

if __name__ == '__main__':
    main()
