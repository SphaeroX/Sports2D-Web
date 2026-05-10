import subprocess
import json
import shutil
from pathlib import Path
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

def get_video_duration(video_path: Path) -> float:
    """Get video duration in seconds using ffprobe."""
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(video_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return float(result.stdout.strip())
    except ValueError:
        return 0.0

def get_video_info(video_path: Path) -> dict:
    """Get video metadata using ffprobe."""
    cmd = [
        "ffprobe", "-v", "error", "-show_format", "-show_streams",
        "-of", "json", str(video_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout)

def create_preview(video_path: Path, output_path: Path, max_height: int = 480) -> Path:
    """Create a downscaled preview video for browser editing."""
    cmd = [
        "ffmpeg", "-y", "-i", str(video_path),
        "-vf", f"scale=-2:{max_height}",
        "-c:v", "libx264", "-preset", "fast", "-crf", "28",
        "-c:a", "aac", "-b:a", "64k",
        "-movflags", "+faststart",
        str(output_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error(f"FFmpeg preview error: {result.stderr}")
        raise RuntimeError("Failed to create preview video")
    return output_path

def trim_video(video_path: Path, output_path: Path, start: float, end: float) -> Path:
    """Trim video to specific time range using FFmpeg (accurate seek)."""
    duration = end - start
    cmd = [
        "ffmpeg", "-y", "-ss", str(start), "-t", str(duration),
        "-i", str(video_path),
        "-c", "copy",
        "-avoid_negative_ts", "make_zero",
        str(output_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        # Fallback to re-encode if copy fails
        cmd = [
            "ffmpeg", "-y", "-ss", str(start), "-t", str(duration),
            "-i", str(video_path),
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac", "-b:a", "128k",
            str(output_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"FFmpeg trim error: {result.stderr}")
            raise RuntimeError("Failed to trim video")
    return output_path

def create_segments(video_path: Path, output_dir: Path, segments: List[Tuple[float, float]]) -> List[Path]:
    """Create trimmed segment videos."""
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for idx, (start, end) in enumerate(segments, 1):
        out = output_dir / f"segment_{idx}.mp4"
        trim_video(video_path, out, start, end)
        paths.append(out)
    return paths
