import cv2
import os
from pathlib import Path

def _infer_fps_and_frames(cap):
    """Try to get FPS and frame count from container; if missing, fall back to manual count."""
    fps = cap.get(cv2.CAP_PROP_FPS)
    nframes = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Some containers don’t report these reliably; patch up if needed.
    if not fps or fps <= 1e-3:
        fps = 30.0  # safe default

    if not nframes or nframes <= 0:
        # Fallback: count by scanning once (costly for long videos, but robust)
        pos = cap.get(cv2.CAP_PROP_POS_FRAMES)
        count = 1  # we already read frame 0 outside
        while True:
            ok, _ = cap.read()
            if not ok:
                break
            count += 1
        # Reset to the beginning for consistency
        cap.set(cv2.CAP_PROP_POS_FRAMES, pos)
        nframes = count
    return float(fps), int(nframes)

def _choose_fourcc(output_path):
    """
    Choose a reasonable FourCC based on extension.
    - .mp4 → 'mp4v' (widely supported in OpenCV builds)
    - .avi → 'MJPG' (huge files but very compatible)
    - otherwise default to 'mp4v'
    """
    ext = output_path.suffix.lower()
    if ext == ".avi":
        return cv2.VideoWriter_fourcc(*"MJPG")
    # Default to mp4v for .mp4 and everything else
    return cv2.VideoWriter_fourcc(*"mp4v")

def freeze_first_frame_cv(in_path, out_path=None, target_fps=None, verbose=True):
    """
    Create a video where every frame is the first frame of the input.
    - in_path: input video path
    - out_path: output video path (default: <stem>_freeze.<ext or .mp4>)
    - target_fps: override FPS (float). If None, try to keep original FPS (or 30 fallback).
    Returns the output path.
    """
    in_path = Path(in_path)
    if out_path is None:
        # Keep same extension if common; else default to .mp4
        ext = in_path.suffix.lower()
        if ext not in (".mp4", ".avi", ".mov", ".mkv"):
            ext = ".mp4"
        out_path = in_path.with_name(in_path.stem + "_freeze" + ext)
    else:
        out_path = Path(out_path)

    cap = cv2.VideoCapture(str(in_path))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {in_path}")

    ok, first = cap.read()
    if not ok or first is None:
        cap.release()
        raise RuntimeError("Could not read the first frame.")

    # Dimensions (ensure even—some codecs prefer even sizes)
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or first.shape[0]
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or first.shape[1]
    w -= (w % 2)
    h -= (h % 2)
    if (w, h) != (first.shape[1], first.shape[0]):
        first = cv2.resize(first, (w, h), interpolation=cv2.INTER_AREA)

    # FPS & total frames
    fps_orig, nframes = _infer_fps_and_frames(cap)
    fps = float(target_fps) if target_fps else fps_orig
    if fps <= 1e-3:
        fps = 30.0

    # Writer
    fourcc = _choose_fourcc(out_path)
    writer = cv2.VideoWriter(str(out_path), fourcc, fps, (w, h))
    if not writer.isOpened():
        cap.release()
        raise RuntimeError("Could not open VideoWriter. Try changing extension or FourCC.")

    # Write the same frame nframes times (or at least 1 second if nframes unknown)
    frames_to_write = max(nframes, int(fps))  # guarantees at least ~1s if container lacked count
    if verbose:
        print(f"[freeze_first_frame_cv] Writing {frames_to_write} frames at {fps:.3f} FPS, size {w}x{h}")
        print(f"[freeze_first_frame_cv] Output: {out_path}")

    for _ in range(frames_to_write):
        writer.write(first)

    writer.release()
    cap.release()
    return str(out_path)

# python make_freeze_vid.py --input ... --output ...

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Freeze entire video to its first frame (OpenCV-only).")
    ap.add_argument("input", help="Input video path")
    ap.add_argument("-o", "--output", help="Output path (default: <input>_freeze.mp4)")
    ap.add_argument("--fps", type=float, default=None, help="Override output FPS (default: keep/or 30)")
    args = ap.parse_args()

    freeze_first_frame_cv(args.input, args.output, args.fps)
