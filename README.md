# Music Player

A modern music player application built with Python and Tkinter, featuring theme switching, album art display, and playlist management.

## Features

- **Music Playback**: Play, pause, stop, and navigate through your music library
- **Theme Switching**: Switch between Dark, Light, and Neon themes with one click
- **Album Art Display**: Displays embedded album artwork from your music files
- **Playlist Management**: Browse and select songs from your music folder
- **Volume Control**: Adjustable volume slider
- **Time Display**: Shows current playback position and total song length
- **Progress Bar**: Visual progress indicator with seek support

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Navigate to the music_player directory:
```bash
cd music_player
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the music player:
```bash
python muisc_player.py
```

### Controls

- **Play**: Start or pause playback
- **Stop**: Stop the current song
- **Next**: Skip to the next song
- **Theme**: Cycle through available themes (Dark → Light → Neon)
- **Volume Slider**: Adjust playback volume (0-100%)
- **Progress Bar**: Click to seek through the song
- **Double-click songs**: Select and play a song from the list

## Themes

### Dark Theme
- Solid dark background (#1e1e1e)
- White text and light UI elements
- Professional and easy on the eyes

### Light Theme
- Minimal background image
- Dark text for contrast
- Clean, bright interface

### Neon Theme
- Neon-colored background image
- Cyan/magenta accent colors
- Modern, vibrant appearance

## Supported Formats

- MP3 (.mp3)
- WAV (.wav)
- OGG Vorbis (.ogg)

## Project Structure

```
music_player/
├── muisc_player.py       # Main application file
├── requirements.txt      # Python dependencies
├── templates/            # Theme configuration files
│   ├── dark.json        # Dark theme settings
│   ├── light.json       # Light theme settings
│   └── neon.json        # Neon theme settings
├── backgrounds/         # Background images for themes
│   ├── minimal.png      # Light theme background
│   ├── neon.png         # Neon theme background
│   └── retro.png        # Alternative background
├── buttons/             # Button images
└── playlists/           # Stored playlists
```

## Dependencies

- **Pillow**: Image processing and display
- **pygame**: Audio playback and mixing
- **mutagen**: Reading music file metadata (ID3 tags)

## Configuration

Themes are defined in JSON format in the `templates/` directory. Each theme file contains:
- Background configuration (color or image)
- UI color settings (text color, button colors, accents)
- Button customization options

You can customize themes by editing these JSON files.

## Troubleshooting

### Music folder not found
- Ensure your music files are in the `~/Music` directory
- Or modify `MUSIC_FOLDER` in the source code

### Theme images not displaying
- Verify image files exist in the `backgrounds/` directory
- Check that image filenames match those specified in theme JSON files

### No audio output
- Ensure pygame mixer is initialized (automatic)
- Check system audio settings
- Verify supported audio format

## Future Enhancements

- Shuffle and repeat modes
- Search/filter songs
- Custom playlists
- Equalizer controls
- Keyboard shortcuts
- Drag-and-drop support
- Recent played tracks

## License

This project is open source and available under the MIT License.

## Author

I'm Kevin and decided to make this code open to use to anyone who has trouble with Spotify and Apple Music

