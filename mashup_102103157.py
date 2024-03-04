import os
import sys
import argparse
from pytube import YouTube
from youtube_search import YoutubeSearch
from moviepy.editor import *
import subprocess

def search_youtube_videos(singer, n):
    print(f"Searching for {n} videos of {singer} on YouTube...")
    query = f"{singer} songs"
    results = YoutubeSearch(query, max_results=n).to_dict()

    video_urls = []
    for i, video in enumerate(results):
        video_url = f"https://youtube.com/watch?v={video['id']}"
        video_urls.append(video_url)
        print(f"Found {i+1}/{n}: {video['title']}")
    
    return video_urls

def download_videos(video_urls, singer):
    print("Downloading videos...")
    for i, url in enumerate(video_urls):
        yt = YouTube(url)
        stream = yt.streams.filter(only_audio=True).first()
        video_path = f"videos/{i+1}_{singer}.mp4"  
        print(f"Downloading {i+1}/{len(video_urls)}: {singer}...")
        if os.path.exists(video_path):
            print(f"Video file {video_path} already exists. Skipping...")
            continue
        stream.download(output_path="videos", filename=f"{i+1}_{singer}.mp4")

def convert_to_audio():
    print("Converting videos to audio...")
    directory = "videos/"
    for filename in os.listdir(directory):
        if filename.endswith(".mp4"):
            video_path = os.path.join(directory, filename)
            audio_path = f"audios/{os.path.splitext(filename)[0]}.mp3"
            if not os.path.exists(audio_path):
                command = ['ffmpeg', '-i', video_path, audio_path]
                subprocess.run(command, capture_output=True, text=True)
                print(f"Converted {video_path} to {audio_path}")
            else:
                print(f"Audio file {audio_path} already exists. Skipping...")

def cut_audio(singer, n, y):
    print(f"Cutting first {y} seconds from all audio files...")
    for i in range(1, n+1):
        audio_path = f"audios/{i}_{singer[:30]}.mp3"
        print(f"Checking audio file: {audio_path}")
        if os.path.exists(audio_path):
            audio = AudioFileClip(audio_path).subclip(0, y)
            audio.write_audiofile(audio_path)
            audio.close()
        else:
            print(f"Error: Audio file {audio_path} not found.")

def merge_audios(singer, n, output_filename):
    print("Merging all audio files...")
    audio_clips = [AudioFileClip(f"audios/{i}_{singer[:30]}.mp3") for i in range(1, n+1)]
    final_clip = concatenate_audioclips(audio_clips)
    final_clip.write_audiofile(output_filename)
    for clip in audio_clips:
        clip.close()

def main():
    parser = argparse.ArgumentParser(description="Mashup Creator")
    parser.add_argument("singer", type=str, help="Name of the singer")
    parser.add_argument("count", type=int, help="Number of videos to download (N > 10)")
    parser.add_argument("duration", type=int, help="Number of seconds to cut from each audio file (Y > 20)")
    parser.add_argument("output", type=str, help="Output filename")
    args = parser.parse_args()

    singer = args.singer
    count = args.count
    duration = args.duration
    output_filename = args.output

    if count <= 3 or duration <= 20:
        print("Count must be greater than 10 and duration must be greater than 20.")
        sys.exit(1)

    if not os.path.exists("videos"):
        os.makedirs("videos")
    if not os.path.exists("audios"):
        os.makedirs("audios")
    if not os.path.exists("output"):
        os.makedirs("output")

    video_urls = search_youtube_videos(singer, count)
    download_videos(video_urls, singer)
    convert_to_audio()
    cut_audio(singer, count, duration)
    merge_audios(singer, count, output_filename)

if __name__ == "__main__":
    main()