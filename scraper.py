
import json
import os
from datetime import datetime
import time
from dotenv import load_dotenv
import lyricsgenius as lg


load_dotenv()


GENIUS_TOKEN = os.getenv('GENIUS_TOKEN')

if not GENIUS_TOKEN:
    print("❌ ОШИБКА: Не найден GENIUS_TOKEN в .env файле!")
    print("Пожалуйста, создай .env файл и добавь строку:")
    print("GENIUS_TOKEN=твой_токен_сюда")
    exit(1)

genius = lg.Genius(GENIUS_TOKEN, skip_non_songs=True, excluded_terms=["(Remix)", "(Cover)"])

genius.verbose = False


class GeniusMusicScraper:
    """Класс для сбора музыкальных данных с Genius"""
    
    def __init__(self, filename='music_data.json'):
        """
        Инициализация скрапера
        
        Args:
            filename (str): Путь к JSON-файлу для сохранения
        """
        self.filename = filename
        self.data = []
        self.load_existing_data()
    
    def load_existing_data(self):
        """Загружает уже существующие данные из JSON файла"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                print(f"✅ Загружены существующие данные ({len(self.data)} артист(ов))")
            except json.JSONDecodeError:
                print(f"⚠️ Файл {self.filename} повреждён, создаю новый...")
                self.data = []
        else:
            print(f"📝 Создаю новый файл {self.filename}")
            self.data = []
    
    def save_data(self):
        """Сохраняет данные в JSON файл"""
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            print(f"✅ Данные сохранены в {self.filename}")
        except Exception as e:
            print(f"❌ Ошибка при сохранении: {e}")
    
    def artist_exists(self, artist_name):
        """Проверяет, есть ли уже артист в базе"""
        return any(a['artist'].lower() == artist_name.lower() for a in self.data)
    
    def search_artist(self, artist_name, max_songs=10):
        """
        Ищет артиста на Genius и собирает его песни
        
        Args:
            artist_name (str): Имя артиста
            max_songs (int): Максимум песен для сбора
        
        Returns:
            dict: Информация об артисте и его песнях
        """
        print(f"\n🎤 Ищу артиста '{artist_name}' на Genius...")
        
        if self.artist_exists(artist_name):
            print(f"⚠️ Артист '{artist_name}' уже в базе!")
            return None
        
        try:
            artist = genius.search_artist(artist_name, max_songs=max_songs)
            
            if not artist:
                print(f"❌ Артист '{artist_name}' не найден на Genius")
                return None
            
            artist_data = {
                "artist": artist.name,
                "country": "Unknown",
                "genius_url": artist.url,
                "image_url": artist.image_url if hasattr(artist, 'image_url') else None,
                "songs": []
            }
            
            print(f"📚 Собираю песни для '{artist.name}'...")
            
            if artist.songs:
                for i, song in enumerate(artist.songs[:max_songs], 1):
                    try:
                        lyrics = song.lyrics if hasattr(song, 'lyrics') and song.lyrics else "Текст недоступен"
                        
                        song_data = {
                            "title": song.title,
                            "year": song.year if hasattr(song, 'year') else None,
                            "lyrics": lyrics,
                            "genius_url": song.url if hasattr(song, 'url') else None,
                            "featured_artists": song.featured_artists if hasattr(song, 'featured_artists') else []
                        }
                        
                        artist_data['songs'].append(song_data)
                        print(f"  ✅ {i}. {song.title}")
                        
                        time.sleep(0.5)
                    
                    except Exception as e:
                        print(f"  ❌ Ошибка при получении песни: {e}")
                        continue
            else:
                print(f"⚠️ Песни не найдены для '{artist.name}'")
                return None
            
            self.data.append(artist_data)
            print(f"\n✅ Артист '{artist.name}' добавлен! Всего песен: {len(artist_data['songs'])}")
            
            return artist_data
        
        except Exception as e:
            print(f"❌ Ошибка при поиске артиста: {e}")
            return None
    
    def search_multiple_artists(self, artist_names, max_songs=5):
        """
        Ищет несколько артистов
        
        Args:
            artist_names (list): Список имён артистов
            max_songs (int): Максимум песен для каждого
        """
        print(f"\n{'='*60}")
        print(f"🎵 НАЧИНАЮ СБОР ДАННЫХ ({len(artist_names)} артист(ов))")
        print(f"{'='*60}\n")
        
        for artist_name in artist_names:
            self.search_artist(artist_name, max_songs=max_songs)
            time.sleep(2)
        
        self.save_data()
        self.print_statistics()
    
    def print_statistics(self):
        """Выводит статистику по собранным данным"""
        total_artists = len(self.data)
        total_songs = sum(len(artist['songs']) for artist in self.data)
        
        print("\n" + "="*60)
        print("📊 СТАТИСТИКА АРХИВА")
        print("="*60)
        print(f"Всего артистов: {total_artists}")
        print(f"Всего песен: {total_songs}")
        
        if total_artists > 0:
            avg_songs = total_songs / total_artists
            print(f"Среднее песен на артиста: {avg_songs:.1f}")
        
        print("\n🎤 Артисты в архиве:")
        for artist in self.data:
            print(f"  • {artist['artist']} — {len(artist['songs'])} песен(и)")
            for song in artist['songs'][:3]:
                print(f"    - {song['title']}")
            if len(artist['songs']) > 3:
                print(f"    ... и ещё {len(artist['songs']) - 3} песен(и)")
        
        print("="*60 + "\n")


def interactive_mode():
    """Интерактивный режим для ввода артистов вручную"""
    scraper = GeniusMusicScraper()
    
    print("\n" + "="*60)
    print("🎵 ИНТЕРАКТИВНЫЙ РЕЖИМ СБОРА МУЗЫКИ")
    print("="*60)
    print("Введи имена артистов по одному (напиши 'exit' для выхода)")
    print("Пример: Imagine Dragons, The Weeknd, Adele\n")
    
    artists = []
    while True:
        artist = input("🎤 Введи имя артиста: ").strip()
        
        if artist.lower() == 'exit':
            break
        
        if artist:
            artists.append(artist)
            print(f"  ✓ '{artist}' добавлен в список\n")
    
    if artists:
        max_songs = input("Сколько песен собрать на артиста? (по умолчанию 5): ").strip()
        max_songs = int(max_songs) if max_songs.isdigit() else 5
        
        scraper.search_multiple_artists(artists, max_songs=max_songs)
    else:
        print("❌ Ты ничего не ввел!")


def main():
    """Главная функция"""
    print("\n" + "="*60)
    print("🎵 GENIUS MUSIC SCRAPER")
    print("Программа для сбора музыки и текстов с Genius.com")
    print("="*60 + "\n")
    
    print("Выбери режим:")
    print("1. Интерактивный (вводишь артистов вручную)")
    print("2. Предзагруженные артисты (популярные исполнители)")
    print("3. Показать статистику")
    
    choice = input("\nВыбор (1/2/3): ").strip()
    
    scraper = GeniusMusicScraper()
    
    if choice == '1':
        interactive_mode()
    
    elif choice == '2':
        popular_artists = [
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

        
        max_songs = input("Сколько песен собрать на артиста? (по умолчанию 3): ").strip()
        max_songs = int(max_songs) if max_songs.isdigit() else 3
        
        scraper.search_multiple_artists(popular_artists, max_songs=max_songs)
    
    elif choice == '3':
        scraper.print_statistics()
    
    else:
        print("❌ Неверный выбор!")


if __name__ == '__main__':
    main()
