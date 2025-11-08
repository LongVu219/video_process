# save as duplicate_each_frame.py
# pip install opencv-python

import cv2
import argparse
from pathlib import Path

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
    if not frames:
        raise RuntimeError("Input video has 0 frames.")
    return frames, fps

def write_video(frames, out_path, fps):
    h, w = frames[0].shape[:2]
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # widely supported
    out = cv2.VideoWriter(str(out_path), fourcc, fps, (w, h))
    if not out.isOpened():
        raise RuntimeError(f"Cannot open output for writing: {out_path}")
    for f in frames:
        out.write(f)
    out.release()

def duplicate_each_frame(frames, factor=2):
    """Return a new list where each frame is repeated `factor` times."""
    if factor < 1:
        raise ValueError("factor must be >= 1")
    out = []
    for f in frames:
        out.extend([f] * factor)
    return out

def main():
    parser = argparse.ArgumentParser(
        description="Duplicate every frame (N -> factor*N). Default factor=2."
    )
    parser.add_argument("input", type=Path, help="Path to input video (e.g., yatch.mp4)")
    parser.add_argument("-o", "--output", type=Path, default=Path("output_dup.mp4"),
                        help="Path to output video (default: output_dup.mp4)")
    parser.add_argument("--factor", type=int, default=2,
                        help="Duplication factor per frame (default: 2)")
    parser.add_argument("--keep-fps", action="store_true",
                        help="Keep original FPS (duration increases by `factor`). "
                             "By default, FPS is multiplied by `factor` to keep duration unchanged.")
    args = parser.parse_args()

    frames, fps = read_all_frames(args.input)
    dup_frames = duplicate_each_frame(frames, factor=args.factor)

    out_fps = fps if args.keep_fps else fps * args.factor
    write_video(dup_frames, args.output, out_fps)

    print(f"Done. Input frames: {len(frames)}, Output frames: {len(dup_frames)}, "
          f"FPS: {out_fps:.2f}. Saved to {args.output}")

if __name__ == "__main__":
    main()
