import tkinter as tk
from tkinter import messagebox, ttk
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
import random
import threading


load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID", "Your client ID from Spotify Developer")
CLIENT_SECRET = os.getenv("CLIENT_SECRET","Your client SECRET from Spotify Developer")
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:8888/callback")

scope = "playlist-modify-public"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope=scope))


class PlaylistGenerator:
    def __init__(self, master):
        self.master = master
        master.title("Генератор плейлистов")
        master.geometry("600x600")  
        master.minsize(600, 600)  


        self.settings_button = ttk.Button(master, text="⚙️ Настройки .env", command=self.open_env_settings)
        self.settings_button.pack(side=tk.TOP, anchor='nw', padx=10, pady=10)

        self.genres = {
            "Поп": ["Dance-pop", "Teen pop", "Electropop", "Synthpop", "K-pop", "Indie pop", "Art pop", "Baroque pop"],
            "Рок": ["Альтернативный рок", "Классический рок", "Панк-рок", "Метал", "Прогрессивный рок", "Инди-рок", "Готик-рок",
                    "Сёрф-рок", "Гарж-рок", "Post-rock", "Hard rock"],
            "Хип-хоп": ["Rap", "Trap", "Boom bap", "Conscious", "Gangsta", "Emo rap", "Lo-fi", "Mumble rap", "Southern rap", "Drill", "Grime"],
            "Электронная": ["House", "Techno", "Trance", "Dubstep", "Drum and Bass", "Electro", "Future Bass", "Ambient", "Downtempo",
                            "IDM", "Hardstyle"],
            "Классическая": ["Классическая", "Симфония", "Опера", "Концерт", "Соната", "Камерная музыка", "Современная классическая", "Барокко",
                             "Романтизм", "Импрессионизм"],
            "Джаз": ["Swing", "Bebop", "Cool Jazz", "Free Jazz", "Acid Jazz", "Latin Jazz", "Smooth Jazz", "Jazz Fusion", "Contemporary jazz"],
            "Регги": ["Roots Reggae", "Dancehall", "Dub", "Lovers Rock", "Ragga", "Rocksteady", "Dub Poetry", "Reggaeton"],
            "Метал": ["Heavy Metal", "Black Metal", "Death Metal", "Thrash Metal", "Doom Metal", "Power Metal", "Symphonic Metal",
                      "Folk Metal", "Metalcore", "Progressive Metal"],
            "Панк": ["Панк-рок", "Поп-панк", "Ска-панк", "Hardcore punk", "Post-punk", "Street punk", "Crust punk", "Skate punk"],
            "Фолк": ["Фолк", "Акустический фолк", "Фолк-рок", "Традиционный фолк", "Кельтский фолк", "Американский фолк", "Скандинавский фолк"],
            "Альтернатива": ["Альтернативный", "Инди", "Гранж", "Пост-гранж", "Фолк-рок", "Экспериментальный рок", "Нью-вейв",
                             "Эмокор", "Синти-поп", "Инди-поп"]
        }

     
        self.genre_frame = ttk.Frame(master, padding="10")
        self.genre_frame.pack(fill=tk.X, pady=5)

        self.label = ttk.Label(self.genre_frame, text="Выберите жанр музыки:")
        self.label.pack(side=tk.LEFT)

        self.genre_combo = ttk.Combobox(self.genre_frame, values=list(self.genres.keys()), state='readonly')
        self.genre_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.genre_combo.current(0)  # Выбор по умолчанию
        self.genre_combo.bind("<<ComboboxSelected>>", self.update_subgenres)

  
        self.subgenre_frame = ttk.Frame(master, padding="10")
        self.subgenre_frame.pack(fill=tk.X, pady=5)

        self.subgenre_label = ttk.Label(self.subgenre_frame, text="Выберите поджанр:")
        self.subgenre_label.pack(side=tk.LEFT)

        self.subgenre_combo = ttk.Combobox(self.subgenre_frame, state='readonly')
        self.subgenre_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.track_count_frame = ttk.Frame(master, padding="10")
        self.track_count_frame.pack(fill=tk.X, pady=5)

        self.track_count_label = ttk.Label(self.track_count_frame, text="Количество треков:")
        self.track_count_label.pack(side=tk.LEFT)

        self.track_count_scale = tk.Scale(self.track_count_frame, from_=1, to=50, orient=tk.HORIZONTAL, length=300, tickinterval=5)
        self.track_count_scale.set(20)  
        self.track_count_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)

  
        self.playlist_frame = ttk.Frame(master, padding="10")
        self.playlist_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.playlist_display = tk.Text(self.playlist_frame, wrap=tk.WORD)
        self.playlist_display.pack(fill=tk.BOTH, expand=True)

       
        self.generate_button = ttk.Button(master, text="Сгенерировать плейлист", command=self.start_generate_playlist_thread)
        self.generate_button.pack(pady=5)

      
        self.create_button = ttk.Button(master, text="Создать плейлист", command=self.create_playlist)
        self.create_button.pack(side=tk.BOTTOM, pady=10)

        self.status_label = ttk.Label(master, text="", foreground="green")
        self.status_label.pack(pady=5)

        self.tracks = []

   
        master.bind("<Configure>", self.on_resize)

    def open_env_settings(self):
        self.env_window = tk.Toplevel(self.master)
        self.env_window.title("Настройки .env")
        self.env_window.geometry("400x300")

        self.client_id_label = ttk.Label(self.env_window, text="CLIENT_ID:")
        self.client_id_label.pack(pady=5)

        self.client_id_entry = ttk.Entry(self.env_window)
        self.client_id_entry.pack(fill=tk.X, padx=5)
        self.client_id_entry.insert(0, CLIENT_ID)

        self.client_secret_label = ttk.Label(self.env_window, text="CLIENT_SECRET:")
        self.client_secret_label.pack(pady=5)

        self.client_secret_entry = ttk.Entry(self.env_window)
        self.client_secret_entry.pack(fill=tk.X, padx=5)
        self.client_secret_entry.insert(0, CLIENT_SECRET)

        self.redirect_uri_label = ttk.Label(self.env_window, text="REDIRECT_URI:")
        self.redirect_uri_label.pack(pady=5)

        self.redirect_uri_entry = ttk.Entry(self.env_window)
        self.redirect_uri_entry.pack(fill=tk.X, padx=5)
        self.redirect_uri_entry.insert(0, REDIRECT_URI)

        
        self.save_button = ttk.Button(self.env_window, text="Сохранить", command=self.save_env_settings)
        self.save_button.pack(pady=10)

    def save_env_settings(self):
        client_id = self.client_id_entry.get()
        client_secret = self.client_secret_entry.get()
        redirect_uri = self.redirect_uri_entry.get()


        with open(".env", "w") as f:
            f.write(f"CLIENT_ID={client_id}\n")
            f.write(f"CLIENT_SECRET={client_secret}\n")
            f.write(f"REDIRECT_URI={redirect_uri}\n")

        messagebox.showinfo("Успех", "Настройки успешно сохранены!")

    def update_subgenres(self, event):
        selected_genre = self.genre_combo.get()
        self.subgenre_combo['values'] = self.genres[selected_genre]
        self.subgenre_combo.current(0)  

    def start_generate_playlist_thread(self):
        thread = threading.Thread(target=self.generate_playlist)
        thread.start()

    def generate_playlist(self):
        genre = self.genre_combo.get()
        subgenre = self.subgenre_combo.get()
        track_count = self.track_count_scale.get()

        self.update_status("Генерация плейлиста...", "blue")

       
        self.tracks = self.get_tracks_by_genre_and_subgenre(genre, subgenre, track_count)

     
        self.master.after(0, self.update_playlist_display)

        self.update_status("Плейлист сгенерирован!", "green")

    def get_tracks_by_genre_and_subgenre(self, genre, subgenre, track_count):
        query = f'genre:"{subgenre}"'
        results = {}
        try:
            results = sp.search(q=query, limit=min(track_count, 50), type='track') 
        except Exception as e:
            print(f"Ошибка при выполнении запроса: {e}")  
            return []

        tracks = results.get('tracks', {}).get('items', [])

        if tracks:

            selected_tracks = random.sample(tracks, min(track_count, len(tracks)))
            return selected_tracks
        else:
            return []

    def update_playlist_display(self):
        self.playlist_display.delete(1.0, tk.END) 
        for track in self.tracks:
            self.playlist_display.insert(tk.END, f"{track['name']} - {', '.join(artist['name'] for artist in track['artists'])}\n")

    def create_playlist(self):
        playlist_name = "Сгенерированный плейлист"
        if not self.tracks:
            messagebox.showerror("Ошибка", "Сначала сгенерируйте плейлист!")
            return
        
        user_id = sp.me()['id']
        playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=True)
        track_ids = [track['id'] for track in self.tracks if 'id' in track]

        if track_ids:
            sp.playlist_add_items(playlist['id'], track_ids)
            messagebox.showinfo("Успех", f"Плейлист '{playlist_name}' успешно создан!")
        else:
            messagebox.showerror("Ошибка", "Не удалось добавить треки в плейлист.")

    def update_status(self, message, color):
        self.status_label.config(text=message, foreground=color)

    def on_resize(self, event):
     
        self.playlist_display.configure(height=event.height // 20) 

if __name__ == "__main__":
    root = tk.Tk()
    app = PlaylistGenerator(root)
    root.mainloop()
