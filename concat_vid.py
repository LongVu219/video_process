# save as concat_videos.py
# pip install opencv-python

import cv2
import argparse
from pathlib import Path

def open_video(p):
    cap = cv2.VideoCapture(str(p))
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {p}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 0.0
    w   = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h   = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    return cap, fps, (w, h)

def read_and_write(cap, writer, target_size=None):
    """Read all frames from cap; optionally resize to target_size; write to writer."""
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if target_size is not None and (frame.shape[1], frame.shape[0]) != target_size:
            frame = cv2.resize(frame, target_size, interpolation=cv2.INTER_AREA)
        writer.write(frame)

def main():
    ap = argparse.ArgumentParser(description="Concatenate two videos end-to-end into one MP4.")
    ap.add_argument("video1", type=Path, help="First input video")
    ap.add_argument("video2", type=Path, help="Second input video")
    ap.add_argument("-o", "--output", type=Path, default=Path("concat.mp4"),
                    help="Output video path (default: concat.mp4)")
    ap.add_argument("--fps", type=float, default=None,
                    help="Output FPS (default: use FPS of the first video, or 25 if unknown)")
    args = ap.parse_args()

    cap1, fps1, size1 = open_video(args.video1)
    cap2, fps2, size2 = open_video(args.video2)

    # Decide output fps
    out_fps = args.fps if args.fps and args.fps > 0 else (fps1 if fps1 and fps1 > 1e-3 else 25.0)

    # Output size = size of video1; resize video2 to match
    out_w, out_h = size1
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(str(args.output), fourcc, out_fps, (out_w, out_h))
    if not out.isOpened():
        cap1.release(); cap2.release()
        raise RuntimeError(f"Cannot open output for writing: {args.output}")

    # Write frames from video1 and then video2
    read_and_write(cap1, out, target_size=(out_w, out_h))     # already matches
    read_and_write(cap2, out, target_size=(out_w, out_h))     # resized if needed

    cap1.release(); cap2.release(); out.release()
    print(f"Saved: {args.output}  (size: {out_w}x{out_h}, fps: {out_fps:.2f})")

if __name__ == "__main__":
    main()
