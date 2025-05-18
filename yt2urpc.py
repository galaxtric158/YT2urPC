import sys
import os
from urllib.parse import urlparse, parse_qs

# Ensure pytubefix is installed
try:
    from pytubefix import YouTube
except ImportError:
    print("ERROR: The Python package 'pytubefix' is not installed.")
    print("Please run:\n    pip install pytubefix")
    sys.exit(1)

def clean_youtube_url(url):
    parsed = urlparse(url)
    query  = parse_qs(parsed.query)
    vid    = query.get('v')
    if vid:
        return f"https://www.youtube.com/watch?v={vid[0]}"
    return url

def unique_path(path):
    base, ext = os.path.splitext(path)
    counter = 1
    new_path = path
    while os.path.exists(new_path):
        new_path = f"{base} ({counter}){ext}"
        counter += 1
    return new_path

def list_available_resolutions(yt):
    streams = yt.streams.filter(progressive=True).order_by('resolution').desc()
    resolutions = []
    seen = set()
    for stream in streams:
        res = stream.resolution
        if res and res not in seen:
            resolutions.append(res)
            seen.add(res)
    return resolutions

def prompt_resolution(available_resolutions):
    """
    Prompt the user to select a resolution from the available options.
    Continues to prompt until a valid selection is made.
    """
    print("Available resolutions:")
    for res in available_resolutions:
        print(f"- {res}")
    print("- high (highest available)")
    print("- low (lowest available)")

    while True:
        choice = input("Enter preferred resolution: ").strip().lower()
        if choice in [res.lower() for res in available_resolutions] or choice in ['high', 'low']:
            return choice
        else:
            print("Invalid resolution. Please try again.")

def download_video(url, out_dir, quality='high', audio_only=False):
    yt = YouTube(url)

    if audio_only:
        stream = (yt.streams
                    .filter(only_audio=True, mime_type="audio/mp4")
                    .order_by('abr')
                    .desc()
                    .first())
        if not stream:
            print(f"No valid audio stream for: {yt.title}")
            return

        print(f"Downloading audio: {yt.title}")
        temp_file = stream.download(output_path=out_dir)

        base, _ = os.path.splitext(temp_file)
        target = unique_path(base + '.mp3')
        os.rename(temp_file, target)
        print(f"Saved MP3 file to: {target}")

    else:
        if quality == 'high':
            stream = yt.streams.get_highest_resolution()
        elif quality == 'low':
            stream = (yt.streams
                        .filter(progressive=True)
                        .order_by('resolution')
                        .first())
        else:
            stream = yt.streams.filter(progressive=True, res=quality).first()

        if not stream:
            print(f"Resolution '{quality}' not available — using highest.")
            stream = yt.streams.get_highest_resolution()

        print(f"Downloading video: {yt.title} ({stream.resolution})")
        stream.download(output_path=out_dir)

    print("Download completed.\n")

def prompt_directory():
    for _ in range(5):
        directory = input("Enter output directory (must already exist): ").strip()
        if os.path.isdir(directory) and os.access(directory, os.W_OK):
            return directory
        else:
            print("Invalid directory. Please try again.")
    print("Continuing with current directory.\n")
    return "."

print("Welcome to galaxtric158's simple YouTube video downloader called YT2urPC.")
video_url = input("Enter a YouTube video URL: ").strip()
video_url = clean_youtube_url(video_url)

download_type = input("Download as (video/mp3): ").strip().lower()
quality = 'high'

yt = YouTube(video_url)

if download_type == 'video':
    available_resolutions = list_available_resolutions(yt)
    quality = prompt_resolution(available_resolutions)

output_dir = prompt_directory()

download_video(
    video_url,
    out_dir=output_dir,
    quality=quality,
    audio_only=(download_type == 'mp3')
)
