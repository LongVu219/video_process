import yt_dlp
import os
import subprocess

#download the video and cut it by ffmpeg (too bad for spp)

def download_and_trim(url, output_path="./video_data"):
    os.makedirs(output_path, exist_ok=True)
    temp_file = os.path.join(output_path, "full.mp4")
    final_file = os.path.join(output_path, "clip.mp4")

    ydl_opts = {
        "format": "bv*[vcodec^=avc1]+ba/best[ext=mp4]",
        "outtmpl": temp_file,
        "merge_output_format": "mp4"
    }


    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # Trim with ffmpeg: from 1s to 25s
    subprocess.run([
        "ffmpeg", "-y",
        "-ss", "4", "-to", "7",
        "-i", temp_file,
        "-c", "copy", final_file
    ])

    print(f"✅ Saved segment to {final_file}")

if __name__ == "__main__":
    download_and_trim("https://www.youtube.com/watch?v=csPc9jLYA5U")
