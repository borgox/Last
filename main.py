import os
import sys
import subprocess
import shlex

venv_path = os.path.join(os.path.dirname(__file__), ".venv")
scripts_path = os.path.join(venv_path, "Scripts")

if not os.path.exists(venv_path):
    os.system("python -m venv .venv") if os.name == "nt" else os.system(
        "python3 -m venv .venv"
    )

if not os.getenv("VIRTUAL_ENV"):
    # If the virtual environment is not activated, activate it and re-run the script
    if os.name == "nt":
        activate_script = os.path.join(scripts_path, "activate.bat")
        args = " ".join(shlex.quote(arg) for arg in sys.argv)
        subprocess.call(f"{activate_script} && python {args}", shell=True)
        sys.exit()  # Exit as the script has been re-run in the new environment
    else:
        # Unix-like systems (Linux, MacOS)
        activate_script = os.path.join(venv_path, "bin", "activate")
        args = " ".join(shlex.quote(arg) for arg in sys.argv)
        subprocess.call(
            f"source {activate_script} && python {args}",
            shell=True,
            executable="/bin/bash",
        )
        sys.exit()
import random
import sys
import time
import re
import shutil
import datetime
import argparse
import pylast
from colorama import Fore, Style, init
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import ctypes
import threading
import yaml


# Initialize Colorama for Windows support
init(autoreset=True)


# Spotify and LastFM Credentials

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

SPOTIFY_CLIENT_ID = config["spotify"]["client_id"]
SPOTIFY_CLIENT_SECRET = config["spotify"]["client_secret"]
LASTFM_API_KEY = config["lastfm"]["api_key"]
LASTFM_API_SECRET = config["lastfm"]["api_secret"]
LASTFM_USERNAME = config["lastfm"]["username"]
LASTFM_PASSWORD_HASH = config["lastfm"]["password_hash"]


class Logger:
    @staticmethod
    def strip_ansi(text: str) -> str:
        ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        return ansi_escape.sub("", text)

    @staticmethod
    def get_true_length(text: str) -> int:
        return len(Logger.strip_ansi(text))

    @staticmethod
    def center_with_ansi(text: str, width: int) -> str:
        true_length = Logger.get_true_length(text)
        padding = max(0, width - true_length)
        left_padding = " " * (padding // 2)
        return f"{left_padding}{text}"

    @staticmethod
    def log(message: str, status: str, status_color: str, end: str = "\n") -> None:
        current_time = datetime.datetime.now().strftime("%m/%d - %H:%M:%S")
        terminal_width = shutil.get_terminal_size().columns
        gradient_colors = [53, 55, 56, 57, 93, 129, 165, 201]
        formatted_time = Logger.apply_gradient(f"[{current_time}]", gradient_colors)
        formatted_status = f"{status_color}[{status}]{Style.RESET_ALL}"
        gradient_message = Logger.apply_gradient(message, [93])
        full_msg = f"{formatted_time} {formatted_status} {gradient_message}"
        print(
            Logger.center_with_ansi(full_msg, terminal_width) + Style.RESET_ALL, end=end
        )

        if end == "":
            sys.stdout.flush()

    @staticmethod
    def input_prompt(prompt: str) -> str:
        Logger.input(prompt)
        return input()

    @staticmethod
    def apply_gradient(text: str, colors: list) -> str:
        return "".join(
            f"\033[38;5;{colors[i % len(colors)]}m{char}" for i, char in enumerate(text)
        )

    @staticmethod
    def success(message: str) -> None:
        Logger.log(message, "SUCCESS", Fore.GREEN)

    @staticmethod
    def error(message: str) -> None:
        Logger.log(message, "ERROR", Fore.RED)

    @staticmethod
    def info(message: str) -> None:
        Logger.log(message, "INFO", Fore.YELLOW)

    @staticmethod
    def input(message: str) -> None:
        message = f"{message} > "
        Logger.log(message, "INPUT", Fore.MAGENTA, end="")


class Banner:
    def __init__(self):
        self.terminal_size = None
        self.banner = r"""
 ▄▀▀▀▀▄      ▄▀▀█▄   ▄▀▀▀▀▄  ▄▀▀▀█▀▀▄ 
█    █      ▐ ▄▀ ▀▄ █ █   ▐ █    █  ▐ 
▐    █        █▄▄▄█    ▀▄   ▐   █     
    █        ▄▀   █ ▀▄   █     █      
  ▄▀▄▄▄▄▄▄▀ █   ▄▀   █▀▀▀    ▄▀       
  █         ▐   ▐    ▐      █         
  ▐                         ▐         
"""
        self.links = "@borgox | .gg/borgo"

    def enable_virtual_terminal(self):
        if os.name == "nt":
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.GetStdHandle(-11)
            mode = ctypes.c_ulong()
            kernel32.GetConsoleMode(handle, ctypes.byref(mode))
            kernel32.SetConsoleMode(handle, mode.value | 0x4)

    def print_banner(self):
        self.enable_virtual_terminal()
        terminal_size = shutil.get_terminal_size()
        self.terminal_size = terminal_size
        banner_lines = self.banner.split("\n")
        gradient_purple = [53, 55, 56, 57, 93, 129, 165, 201]

        for i, line in enumerate(banner_lines):
            color_index = gradient_purple[i % len(gradient_purple)]
            print(f"\033[38;5;{color_index}m{line.center(terminal_size.columns)}")

        self.print_alternating_color_text(
            self.links, (terminal_size.columns - len(self.links)) // 2
        )
        print("\033[0m")

    def print_alternating_color_text(self, text, center):
        color1, color2 = 93, 57
        for i, char in enumerate(text.center(self.terminal_size.columns)):
            color_code = color1 if i % 2 == 0 else color2
            print(f"\033[38;5;{color_code}m{char}", end="")


class MultiTool:
    def __init__(self):
        os.system("cls" if os.name == "nt" else "clear")
        self.banner = Banner()
        self.banner.print_banner()
        self.spotify_oauth = None
        self.spotify = Spotify(
            client_credentials_manager=SpotifyClientCredentials(
                client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET
            ),
            auth_manager=self.spotify_oauth,
        )
        self.network = pylast.LastFMNetwork(
            api_key=LASTFM_API_KEY,
            api_secret=LASTFM_API_SECRET,
            username=LASTFM_USERNAME,
            password_hash=LASTFM_PASSWORD_HASH,
        )

        self.completed_count = 0
        self.progress_lock = threading.Lock()

    def get_track_info_from_spotify(self, url):
        track_id = url.split("/")[-1].split("?")[0]
        track_info = self.spotify.track(track_id)
        artist_name = track_info["artists"][0]["name"]
        track_title = track_info["name"]
        return artist_name, track_title

    def rate_limited_scrobble(self, artist, title, **kwargs):
        # Perform the scrobble
        timestamp = int(time.time())
        try:
            self.network.scrobble(artist, title, timestamp=timestamp, **kwargs)
            self.completed_count += 1
            time.sleep(1)
        except Exception as e:
            if "try again" in str(e):
                time.sleep(random.randint(1, 4))
                self.rate_limited_scrobble(artist, title, **kwargs)
            Logger.error(f"Scrobble failed: {str(e)}")

    def gradient_progress_bar(self, count, total, start_time):
        gradient_colors = [53, 55, 56, 57, 93, 129, 165, 201]
        progress = count / total

        terminal_width = shutil.get_terminal_size().columns

        # Fixed width components
        time_width = 20  # "Time Taken: 00:00:00"
        percentage_width = 5  # "100% "
        brackets_width = 2  # "[]"
        spacing_width = 4  # Spaces between components

        max_bar_width = terminal_width - (
            time_width + percentage_width + brackets_width + spacing_width
        )
        bar_width = min(max(30, max_bar_width), 60)

        filled_length = int(bar_width * progress)
        filled_bar = "".join(
            f"\033[38;5;{gradient_colors[i % len(gradient_colors)]}m█"
            for i in range(filled_length)
        )
        empty_bar = "\033[38;5;236m" + "─" * (bar_width - filled_length)
        bar = filled_bar + empty_bar + "\033[0m"

        elapsed_time = int(time.time() - start_time)
        elapsed_str = str(datetime.timedelta(seconds=elapsed_time))

        progress_text = f"[{bar}] {int(progress * 100):3d}% | Time: {elapsed_str}"

        padding = " " * ((terminal_width - len(Logger.strip_ansi(progress_text))) // 2)
        final_text = f"\r{padding}{progress_text}"

        sys.stdout.write(final_text)
        sys.stdout.flush()
        # Update title with count and time elapsed along with name "Last" so like "Last | 1/10 | 00:00:00"
        ctypes.windll.kernel32.SetConsoleTitleW(
            f"@Last | {count}/{total} | {elapsed_str} | Made by @borghetoo"
        )

        if count == total:
            sys.stdout.write("\n")
            sys.stdout.flush()

    def run(self, artist, title, count=1, **kwargs):
        for i in range(count):
            self.rate_limited_scrobble(artist, title, **kwargs)

    def multiple_scrobbles(self, artist, title, count=1, **kwargs):
        start_time = time.time()
        self.completed_count = 0

        t = threading.Thread(
            target=self.run, args=(artist, title, count), kwargs=kwargs
        )
        t.start()

        # Monitor progress
        while self.completed_count < count:
            self.gradient_progress_bar(self.completed_count, count, start_time)
            time.sleep(0.1)

        # Final progress update
        self.gradient_progress_bar(count, count, start_time)

        t.join()
        print()
        Logger.success(f"Completed {count} scrobbles for {artist} - {title}")
        Logger.input("Press ENTER to exit")

    def interactive_mode(self, count=1):
        spotify_url = Logger.input_prompt(
            "Enter Spotify Track URL (leave blank for manual entry)"
        )
        if spotify_url:
            artist, title = self.get_track_info_from_spotify(spotify_url)
            Logger.info(f"Found track: {artist} - {title}")
        else:
            artist = Logger.input_prompt("Enter Artist Name")
            title = Logger.input_prompt("Enter Track Title")
        self.multiple_scrobbles(artist, title, count)

    def parse_arguments(self):
        parser = argparse.ArgumentParser(description="Multitool for LastFM Scrobbling.")
        parser.add_argument("-s", "--spotify", type=str, help="Spotify track URL")
        parser.add_argument("-a", "--artist", type=str, help="Artist name")
        parser.add_argument("-t", "--title", type=str, help="Track title")
        parser.add_argument("--album", type=str, help="Album name", default=None)
        parser.add_argument(
            "--album_artist", type=str, help="Album artist name", default=None
        )
        parser.add_argument(
            "--track_number", type=int, help="Track number", default=None
        )
        parser.add_argument("--duration", type=int, help="Track duration", default=None)
        parser.add_argument("--stream_id", type=str, help="Stream ID", default=None)
        parser.add_argument("--context", type=str, help="Context", default=None)
        parser.add_argument("--mbid", type=str, help="MusicBrainz ID", default=None)
        parser.add_argument("--count", type=int, default=1, help="Number of scrobbles")
        args = parser.parse_args()
        if args.spotify:
            artist, title = self.get_track_info_from_spotify(args.spotify)
            self.multiple_scrobbles(
                artist,
                title,
                count=args.count,
                album=args.album,
                album_artist=args.album_artist,
                track_number=args.track_number,
                duration=args.duration,
                stream_id=args.stream_id,
                context=args.context,
                mbid=args.mbid,
            )
        elif args.artist and args.title:
            self.multiple_scrobbles(
                args.artist,
                args.title,
                count=args.count,
                album=args.album,
                album_artist=args.album_artist,
                track_number=args.track_number,
                duration=args.duration,
                stream_id=args.stream_id,
                context=args.context,
                mbid=args.mbid,
            )
        else:
            self.interactive_mode(count=args.count)


if __name__ == "__main__":
    tool = MultiTool()
    tool.parse_arguments()
