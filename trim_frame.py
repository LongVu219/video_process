import os
import subprocess

def trim_by_frames(input_path, output_path="clip.mp4", start_frame=0, end_frame=80):
    subprocess.run([
        "ffmpeg", "-y",
        "-i", input_path,
        "-vf", f"select='between(n\\,{start_frame}\\,{end_frame})',setpts=PTS-STARTPTS",
        "-an",  # drop audio
        output_path
    ])
    print(f"✅ Saved frames {start_frame}–{end_frame} to {output_path}")



if __name__ == "__main__":
    trim_by_frames("/prj/corp/airesearch/lasvegas/vol5-scratch/users/phongnh/Long/prj-chronos/example_test_data/videos/true2.mp4", "clip.mp4", 0, 80)