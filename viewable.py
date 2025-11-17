# fix_mp4.py
# Colab tip (once per session):
# !apt-get -y install ffmpeg

import subprocess
import shlex
import argparse
import os
import sys

def run(cmd):
    print(">>", cmd)
    proc = subprocess.run(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    print(proc.stdout)
    return proc.returncode == 0

def ensure_ext(path, ext=".mp4"):
    root, e = os.path.splitext(path)
    return path if e.lower() == ext else root + ext

def fix_mp4(input_mp4, output_mp4=None, force_transcode=False):
    """
    Try stream-copy (no re-encode) with moov-faststart and generated PTS.
    If that fails or force_transcode=True, re-encode to H.264/AAC.
    """
    if not os.path.exists(input_mp4):
        raise FileNotFoundError(input_mp4)
    if output_mp4 is None:
        base, _ = os.path.splitext(input_mp4)
        output_mp4 = base + "_fixed.mp4"
    output_mp4 = ensure_ext(output_mp4)

    # 1) Lossless remux (no quality change)
    # -fflags +genpts         : generate timestamps if missing
    # -c copy                 : copy audio/video as-is (no re-encode)
    # -map 0                  : keep all streams
    # -movflags +faststart    : move moov atom to front (better playback)
    # -ignore_unknown         : skip unknown streams instead of failing
    remux_cmd = (
        f'ffmpeg -y -fflags +genpts -i "{input_mp4}" '
        f'-map 0 -c copy -movflags +faststart -ignore_unknown 1 '
        f'"{output_mp4}"'
    )

    if not force_transcode and run(remux_cmd):
        print(f"[OK] Remuxed (no quality change): {output_mp4}")
        return output_mp4

    # 2) Fallback: re-encode (very compatible H.264/AAC)
    # -pix_fmt yuv420p        : widest compatibility
    # -vsync 2                : drop/dupe to fix timestamp issues
    # -movflags +faststart    : better web playback
    # Adjust CRF/preset for different size/quality trade-offs
    trans_cmd = (
        f'ffmpeg -y -fflags +genpts -i "{input_mp4}" '
        f'-map 0:v:0 -map 0:a? '
        f'-c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p '
        f'-c:a aac -b:a 192k -movflags +faststart -vsync 2 '
        f'"{output_mp4}"'
    )
    if run(trans_cmd):
        print(f"[OK] Transcoded (H.264/AAC): {output_mp4}")
        return output_mp4

    raise RuntimeError("Both remux and transcode paths failed.")

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Repair/normalize an MP4 for better playback.")
    p.add_argument("input", help="Path to input .mp4")
    p.add_argument("-o", "--output", default=None, help="Output .mp4 path (default: *_fixed.mp4)")
    p.add_argument("--force-transcode", action="store_true",
                   help="Skip remux and directly re-encode (H.264/AAC).")
    args = p.parse_args()

    try:
        out = fix_mp4(args.input, args.output, force_transcode=args.force_transcode)
        print("Saved:", out)
    except Exception as e:
        print("ERROR:", e)
        sys.exit(1)
