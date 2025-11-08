# save as make_81_frames.py
# pip install opencv-python

import cv2
import argparse
from pathlib import Path

TARGET_FRAMES = 81

def read_all_frames(video_path):
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    if not fps or fps <= 1e-3:
        fps = 25.0  # sensible default

    frames = []
    ok, frame = cap.read()
    while ok:
        frames.append(frame)
        ok, frame = cap.read()

    cap.release()
    return frames, fps

def write_video(frames, out_path, fps):
    if len(frames) == 0:
        raise RuntimeError("No frames to write.")
    h, w = frames[0].shape[:2]
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # widely supported
    out = cv2.VideoWriter(str(out_path), fourcc, fps, (w, h))
    if not out.isOpened():
        raise RuntimeError(f"Cannot open output for writing: {out_path}")

    for f in frames:
        out.write(f)
    out.release()

def ensure_81_frames(frames, truncate=False):
    n = len(frames)
    if n == 0:
        raise RuntimeError("Input video has 0 frames.")

    if n < TARGET_FRAMES:
        last = frames[-1]
        # append the last frame until we reach 81
        frames = frames + [last] * (TARGET_FRAMES - n)
    elif truncate and n > TARGET_FRAMES:
        frames = frames[:TARGET_FRAMES]
    # else: leave as-is (>=81) when not truncating
    return frames

def main():
    parser = argparse.ArgumentParser(description="Pad a video to 81 frames by repeating the last frame.")
    parser.add_argument("input", type=Path, help="Path to input video (e.g., yatch.mp4)")
    parser.add_argument("-o", "--output", type=Path, default=Path("output_81.mp4"),
                        help="Path to output video (default: output_81.mp4)")
    parser.add_argument("--truncate", action="store_true",
                        help="If set, truncate videos longer than 81 frames to exactly 81.")
    args = parser.parse_args()

    frames, fps = read_all_frames(args.input)
    frames = ensure_81_frames(frames, truncate=args.truncate)
    write_video(frames, args.output, 16)

    print(f"Done. Saved to {args.output} ({len(frames)} frames at 16 fps).")

if __name__ == "__main__":
    main()
