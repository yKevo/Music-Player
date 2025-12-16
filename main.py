import os
import sys
import json
import time
import random
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, Listbox
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont, ImageTk
import pygame
from mutagen import File as MutagenFile


# Configuration

MUSIC_FOLDER = os.path.expanduser("~/Music")
SUPPORTED_EXTS = (".mp3", ".wav", ".ogg")

ART_SIZE = (250, 250)
AUTO_REFRESH_MS = 5000
POLL_MS = 700


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(SCRIPT_DIR, "templates")
BACKGROUNDS_DIR = os.path.join(SCRIPT_DIR, "backgrounds")
BUTTONS_DIR = os.path.join(SCRIPT_DIR, "buttons")


# Utility Functions


def fmt_time(seconds: float) -> str:
    seconds = max(0, int(seconds))
    return f"{seconds//60:02}:{seconds%60:02}"


def extract_embedded_art(path: str):
    try:
        audio = MutagenFile(path)
        tags = getattr(audio, "tags", None)
        if not tags:
            return None
        for tag in tags.values():
            data = getattr(tag, "data", None)
            if isinstance(data, (bytes, bytearray)):
                return BytesIO(data)
    except Exception:
        pass
    return None




def ensure_dirs_and_samples():
    os.makedirs(TEMPLATES_DIR, exist_ok=True)
    os.makedirs(BACKGROUNDS_DIR, exist_ok=True)
    os.makedirs(BUTTONS_DIR, exist_ok=True)


    dark_theme = {
        "name": "Dark",
        "bg": {"type": "color", "value": "#1e1e1e", "mode": "stretch"},
        "ui": {
            "primary_text": "#ffffff",
            "button_bg": "#3c3c3c",
            "accent": "#007acc",
        },
        "buttons": {}
    }

    theme_path = os.path.join(TEMPLATES_DIR, "dark.json")
    if not os.path.exists(theme_path):
        with open(theme_path, "w", encoding="utf-8") as f:
            json.dump(dark_theme, f, indent=2)

    # Placeholder buttons
    btn_shapes = {
        "play.png": lambda d: d.polygon([(20,10),(90,32),(20,54)], fill="white"),
        "pause.png": lambda d: (
            d.rectangle((20,10,40,54), fill="white"),
            d.rectangle((60,10,80,54), fill="white")
        ),
        "stop.png": lambda d: d.rectangle((25,15,85,55), fill="white")
    }

    for name, draw_fn in btn_shapes.items():
        path = os.path.join(BUTTONS_DIR, name)
        if not os.path.exists(path):
            img = Image.new("RGBA", (110, 64), (40,40,40,255))
            d = ImageDraw.Draw(img)
            draw_fn(d)
            img.save(path)



class MusicPlayer:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Python Music Player")
        self.root.geometry("900x820")

        pygame.mixer.init()

        self.music_folder = MUSIC_FOLDER
        self.playlist = []
        self.current_index = -1

        self.playing = False
        self.paused = False

        self.song_length = 0
        self.play_start_ms = 0
        self.played_seconds = 0

        self._load_templates()
        self.current_theme_index = 0
        self.theme_names = sorted(self.templates.keys())
        self._build_ui()
        self.load_songs(self.music_folder)
        self._apply_theme()

        self.root.after(POLL_MS, self._poll)


    # UI Construction

    def _build_ui(self):
        self.bg_canvas = tk.Canvas(self.root, highlightthickness=0)
        self.bg_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.listbox = Listbox(self.root, bg="#252526", fg="white", height=12)
        self.listbox.pack(pady=10)
        self.listbox.bind("<Double-Button-1>", self._on_select)

        self.album_label = tk.Label(self.root)
        self.album_label.pack(pady=10)

        controls = tk.Frame(self.root, bg="")
        controls.pack(pady=10)

        self.play_btn = tk.Button(controls, text="Play", width=10, command=self.toggle_play)
        self.play_btn.grid(row=0, column=0, padx=5)

        self.stop_btn = tk.Button(controls, text="Stop", width=10, command=self.stop)
        self.stop_btn.grid(row=0, column=1, padx=5)
        
        self.next_btn = tk.Button(controls, text="Next", width=10, command=self.next)
        self.next_btn.grid(row=0, column=2, padx=5)
        
        self.theme_btn = tk.Button(controls, text="Theme", width=10, command=self._switch_theme)
        self.theme_btn.grid(row=0, column=3, padx=5)
        
        self.control_buttons = [self.play_btn, self.stop_btn, self.next_btn, self.theme_btn]

        self.progress = tk.Scale(self.root, from_=0, to=100, orient="horizontal", length=700)
        self.progress.pack(pady=10)

        self.time_label = tk.Label(self.root, text="00:00 / 00:00")
        self.time_label.pack()

        self.volume = tk.Scale(self.root, from_=0, to=100, orient="horizontal", label="Volume",
                               command=lambda v: pygame.mixer.music.set_volume(int(v)/100))
        self.volume.set(70)
        self.volume.pack(pady=10)


    # Themes

    def _apply_theme(self):
        """Apply the current theme to the UI and background."""
        try:
            theme_name = self.theme_names[self.current_theme_index]
            theme = self.templates[theme_name]
            
            # Update theme button to show current theme
            self.theme_btn.config(text=f"Theme: {theme_name}")
            
            # Apply background
            bg_config = theme.get("bg", {})
            bg_type = bg_config.get("type", "color")
            
            # Clear canvas
            self.bg_canvas.delete("all")
            
            if bg_type == "color":
                color = bg_config.get("value", "#1e1e1e")
                self.bg_canvas.config(bg=color)
                self.root.config(bg=color)
            elif bg_type == "image":
                img_file = bg_config.get("value", "")
                img_path = os.path.join(BACKGROUNDS_DIR, img_file)
                if os.path.exists(img_path):
                    img = Image.open(img_path)
                    mode = bg_config.get("mode", "stretch")
                    
                    if mode == "stretch":
                        img = img.resize((900, 820))
                    elif mode == "center":
                        pass  # Keep original size, will be centered on canvas
                    
                    self.bg_image = ImageTk.PhotoImage(img)
                    self.bg_canvas.create_image(450, 410, image=self.bg_image, anchor="center")
                    self.bg_canvas.config(bg="black")
            
            # Apply UI colors
            ui_config = theme.get("ui", {})
            primary_color = ui_config.get("primary_text", "#ffffff")
            button_bg = ui_config.get("button_bg", "#3c3c3c")
            bg_color = bg_config.get("value", "#1e1e1e") if bg_type == "color" else "black"
            
            self.listbox.config(bg=button_bg, fg=primary_color)
            self.time_label.config(fg=primary_color, bg=bg_color)
            self.album_label.config(bg=bg_color)
            
            # Update all control buttons
            for button in self.control_buttons:
                button.config(fg=primary_color, bg=button_bg, activebackground=button_bg, activeforeground=primary_color)
        except Exception as e:
            print(f"Error applying theme: {e}")
            import traceback
            traceback.print_exc()
    
    def _switch_theme(self):
        """Switch to the next available theme."""
        try:
            self.current_theme_index = (self.current_theme_index + 1) % len(self.theme_names)
            self._apply_theme()
            print(f"Switched to theme: {self.theme_names[self.current_theme_index]}")
        except Exception as e:
            print(f"Error switching theme: {e}")
            import traceback
            traceback.print_exc()


    # Templates

    def _load_templates(self):
        self.templates = {}
        for f in os.listdir(TEMPLATES_DIR):
            if f.endswith(".json"):
                with open(os.path.join(TEMPLATES_DIR, f), "r") as file:
                    data = json.load(file)
                    self.templates[data["name"]] = data


    # Playlist

    def load_songs(self, folder: str):
        if not os.path.isdir(folder):
            return
        self.playlist = [
            os.path.join(folder, f)
            for f in os.listdir(folder)
            if f.lower().endswith(SUPPORTED_EXTS)
        ]
        self.listbox.delete(0, tk.END)
        for song in self.playlist:
            self.listbox.insert(tk.END, os.path.basename(song))


    def toggle_play(self):
        if not self.playlist:
            return

        if not self.playing:
            if self.current_index == -1:
                self.current_index = 0
                self._load_current()
            pygame.mixer.music.play()
            self.playing = True
            self.play_btn.config(text="Pause")
        else:
            pygame.mixer.music.pause()
            self.playing = False
            self.play_btn.config(text="Play")

    def stop(self):
        pygame.mixer.music.stop()
        self.playing = False
        self.play_btn.config(text="Play")

    def next(self):
        if not self.playlist:
            return
        self.current_index = (self.current_index + 1) % len(self.playlist)
        self._load_current()
        pygame.mixer.music.play()
        self.playing = True

    def _load_current(self):
        path = self.playlist[self.current_index]
        pygame.mixer.music.load(path)

        try:
            audio = MutagenFile(path)
            self.song_length = int(audio.info.length)
        except Exception:
            self.song_length = 0

        self.progress.config(to=self.song_length)
        self._set_album_art(path)
    

    def _set_album_art(self, path):
        art = extract_embedded_art(path)
        img = None

        if art:
            img = Image.open(art)
        else:
            img = Image.new("RGBA", ART_SIZE, (40,40,40))

        img.thumbnail(ART_SIZE)
        self.album_img = ImageTk.PhotoImage(img)
        self.album_label.config(image=self.album_img)


    def _poll(self):
        try:
            pos = pygame.mixer.music.get_pos() // 1000
            if pos >= 0:
                self.progress.set(pos)
                self.time_label.config(text=f"{fmt_time(pos)} / {fmt_time(self.song_length)}")
        except Exception:
            pass
        self.root.after(POLL_MS, self._poll)


    def _on_select(self, _):
        sel = self.listbox.curselection()
        if sel:
            self.current_index = sel[0]
            self._load_current()
            pygame.mixer.music.play()
            self.playing = True
            self.play_btn.config(text="Pause")


if __name__ == "__main__":
    ensure_dirs_and_samples()
    root = tk.Tk()
    MusicPlayer(root)
    root.mainloop()
