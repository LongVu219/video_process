# save as save_last_frame.py
# pip install opencv-python

import cv2
import argparse
from pathlib import Path

def read_last_frame(video_path):
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video_path}")

    # Try random access using frame count
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    last = None

    if frame_count and frame_count > 0:
        # Some codecs require seeking to frame_count - 2 (last keyframe before final)
        # We'll try a couple positions from the end.
        for back in (1, 2, 3, 5):
            idx = max(frame_count - back, 0)
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ok, frame = cap.read()
            if ok:
                last = frame
                break
        # If read failed, fall back to sequential scan below
    if last is None:
        # Fallback: sequentially read to the end
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ok, frame = cap.read()
        if not ok:
            cap.release()
            raise RuntimeError("Input video has 0 readable frames.")
        last = frame
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            last = frame

    cap.release()
    return last

def save_jpg(image, out_path, quality=95):
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # OpenCV expects BGR → JPEG is fine directly
    ok = cv2.imwrite(str(out_path), image, [int(cv2.IMWRITE_JPEG_QUALITY), int(quality)])
    if not ok:
        raise RuntimeError(f"Failed to write image: {out_path}")

def main():
    parser = argparse.ArgumentParser(description="Save the last frame of a video as a JPG image.")
    parser.add_argument("input", type=Path, help="Path to input video (e.g., clip.mp4)")
    parser.add_argument("-o", "--output", type=Path, default=Path("last_frame.jpg"),
                        help="Output JPG path (default: last_frame.jpg)")
    parser.add_argument("--quality", type=int, default=95,
                        help="JPEG quality 1-100 (default: 95)")
    args = parser.parse_args()

    last_frame = read_last_frame(args.input)
    save_jpg(last_frame, args.output, quality=args.quality)
    print(f"Saved last frame to {args.output}")

if __name__ == "__main__":
    main()
