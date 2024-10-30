# MultiTool README

## Overview
Last is a Python application designed for scrobbling music to LastFM. It utilizes Spotify integration to fetch track information automatically or lets you manually input artist and title details. The tool also includes a dynamic console banner and a color-logging system for better user experience. Virtual environment management and easy installation are part of its features.

## Features
- Scrobble tracks to LastFM either manually or via a Spotify track URL.
- Virtual environment setup for easy dependency management.
- Gradient-based console progress bars and banner.
- Supports both interactive and command-line modes.

## Prerequisites
- Python 3.7+
- Spotify API credentials (Client ID and Client Secret)
- LastFM API credentials (API Key, API Secret, Username, and Password Hash)

## Installation

### Step 1: Clone the Repository
```
git clone https://github.com/borgox/last.git
cd multitool
```

### Step 2: Virtual Environment Setup
The script will automatically create and activate a virtual environment.
- Windows:
  ```
  python -m venv .venv
  .venv\Scripts\activate
  ```
- Unix/macOS:
  ```
  python3 -m venv .venv
  source .venv/bin/activate
  ```

### Step 3: Install Dependencies
Install the required Python dependencies using pip:
```
pip install -r requirements.txt
```

## Configuration

### Step 4: Set Up Your Credentials
Create a `config.yaml` file in the project if not existing already root with the following format:
```yaml
spotify:
  client_id: YOUR_SPOTIFY_CLIENT_ID
  client_secret: YOUR_SPOTIFY_CLIENT_SECRET

lastfm:
  api_key: YOUR_LASTFM_API_KEY
  api_secret: YOUR_LASTFM_API_SECRET
  username: YOUR_LASTFM_USERNAME
  password_hash: YOUR_LASTFM_PASSWORD_HASH
```
Ensure you replace `YOUR_SPOTIFY_CLIENT_ID`, `YOUR_LASTFM_API_KEY`, etc., with your actual credentials.

## Usage
The tool can be run in both interactive and command-line modes.

### Step 1: Activate Virtual Environment
Before running the script, ensure the virtual environment is activated.

### Command-Line Mode
You can specify the artist, title, or a Spotify URL directly via the command line:
```
python multitool.py --spotify <SPOTIFY_TRACK_URL> --count <NUMBER_OF_SCROBBLES>
```
Or specify the artist and title manually:
```
python multitool.py --artist "Artist Name" --title "Track Title" --count 5
```

### Interactive Mode
If you run the tool without any arguments, it will prompt you for details in an interactive manner:
```
python main.py
```

## Running the Application
Once your configuration file is ready and your virtual environment is activated, simply run the `main.py` script to start scrobbling:
```
python main.py
```

## Dependencies
- `pylast`: for interacting with the LastFM API.
- `spotipy`: for Spotify integration.
- `colorama`: for terminal color output.
- `PyYAML`: for loading credentials from `config.yaml`.

To install these dependencies manually, you can run:
```
pip install pylast spotipy colorama pyyaml
```

## Examples
### Scrobble a Track from Spotify
```
python main.py --spotify "https://open.spotify.com/track/xyz" --count 3
```
### Scrobble Manually Entered Track
```
python main.py --artist "Daft Punk" --title "One More Time" --count 5
```

## Notes
- The script will automatically activate the virtual environment if not already activated.
- Windows users: Make sure to run commands from a terminal with proper permissions to avoid issues with environment activation.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Credits
- Developed by [borgo] - Made with love and Python.


## Issues
If you encounter any issues, please open an issue on GitHub or reach out to me directly.

--------
[AI Generated README Because this is not a big project]
