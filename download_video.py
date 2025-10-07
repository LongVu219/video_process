from pytube import YouTube
import os

def download_youtube_video(url: str, output_path: str):
    """
    Download a YouTube video to the given local path.

    Args:
        url (str): YouTube video URL.
        output_path (str): Folder path where the video will be saved.
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_path, exist_ok=True)

        # Initialize YouTube object
        yt = YouTube(url)
        print(f"Title: {yt.title}")
        print(f"Author: {yt.author}")
        print("Downloading...")

        # Get the highest resolution stream
        stream = yt.streams.get_highest_resolution()

        # Download video
        stream.download(output_path=output_path)

        print(f"✅ Download completed: {os.path.join(output_path, yt.title)}.mp4")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    video_url = input("Enter YouTube URL: ").strip()
    save_path = input("Enter local save path (e.g., C:/Videos or ./videos): ").strip()
    download_youtube_video(video_url, save_path)
