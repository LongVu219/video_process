# save as resize_to_81_frames.py
# pip install opencv-python

import cv2
import argparse
from pathlib import Path

TARGET = 81

def open_video(path: Path):
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {path}")
    fps = cap.get(cv2.CAP_PROP_FPS)
    if not fps or fps <= 1e-3:
        fps = 25.0  # sensible default if metadata missing
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or None
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or None
    return cap, fps, (w, h)

def parse_size(size_str: str):
    try:
        w, h = size_str.lower().split("x")
        return int(w), int(h)
    except Exception:
        raise argparse.ArgumentTypeError("Size must be like 1920x1080")

def write_video(frames, out_path: Path, fps: float, size=None):
    if not frames:
        raise RuntimeError("No frames to write.")
    h, w = frames[0].shape[:2]
    if size is None:
        out_size = (w, h)
    else:
        out_size = size
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(str(out_path), fourcc, fps, out_size)
    if not out.isOpened():
        raise RuntimeError(f"Cannot open output for writing: {out_path}")

    for f in frames:
        if out_size != (f.shape[1], f.shape[0]):
            f = cv2.resize(f, out_size, interpolation=cv2.INTER_AREA)
        out.write(f)
    out.release()

def make_81_frames(cap, target=TARGET):
    frames = []
    last = None
    # Read up to target frames
    for _ in range(target):
        ok, frame = cap.read()
        if not ok:
            break
        frames.append(frame)
        last = frame
    # If we already got target frames, done (truncate naturally)
    if len(frames) == target:
        return frames
    # Otherwise, we reached EOF early; pad with the last available frame
    if last is None:
        raise RuntimeError("Input video has 0 readable frames.")
    frames.extend([last] * (target - len(frames)))
    return frames

def main():
    ap = argparse.ArgumentParser(
        description="Force any video to exactly 81 frames (truncate or pad with last frame)."
    )
    ap.add_argument("input", type=Path, help="Input video path")
    ap.add_argument("-o", "--output", type=Path, default=Path("video_81.mp4"),
                    help="Output video path (default: video_81.mp4)")
    ap.add_argument("--fps", type=float, default=None,
                    help="Output FPS (default: use input FPS or 25 if unknown)")
    ap.add_argument("--size", type=parse_size, default=None,
                    help="Optional output size WxH (e.g., 1920x1080). By default keep input size.")
    args = ap.parse_args()

    cap, in_fps, in_size = open_video(args.input)
    out_fps = args.fps if (args.fps and args.fps > 0) else in_fps

    frames = make_81_frames(cap, target=TARGET)
    cap.release()

    write_video(frames, args.output, out_fps, size=args.size)
    print(f"Saved {len(frames)} frames to {args.output}  "
          f"({(args.size or (in_size[0], in_size[1]))[0]}x{(args.size or (in_size[0], in_size[1]))[1]} @ {out_fps:.2f} fps)")

if __name__ == "__main__":
    main()
