"""FFmpeg multi-track video composition service."""
import subprocess
from pathlib import Path
from typing import Optional
import ffmpeg
from app.utils.file_utils import TempDir


def compose_video(
    video_clips: list[str],
    audio_tracks: list[dict],
    output_path: str,
    width: int = 1920,
    height: int = 1080,
    fps: int = 24,
    subtitle_file: Optional[str] = None,
) -> str:
    """Compose video clips and audio tracks into a final MP4.

    Uses FFmpeg filter_complex for multi-track mixing.

    Args:
        video_clips: List of local file paths to video clips (in order).
        audio_tracks: List of dicts with keys: path, volume, start_time, type.
        output_path: Output MP4 file path.
        width: Output width in pixels.
        height: Output height in pixels.
        fps: Output frame rate.
        subtitle_file: Optional SRT subtitle file path.

    Returns:
        Absolute path to the generated output file.
    """
    if not video_clips:
        raise ValueError("No video clips provided")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Build concat list file
    with TempDir() as tmp_dir:
        concat_file = Path(tmp_dir) / "concat.txt"
        concat_lines = []
        for clip_path in video_clips:
            concat_lines.append(f"file '{clip_path}'\n")
        concat_file.write_text("".join(concat_lines))

        # Build FFmpeg command using filter_complex
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0", "-i", str(concat_file),
        ]

        # Add audio inputs
        for track in audio_tracks:
            cmd.extend(["-i", track["path"]])

        # Video scale filter
        filter_parts = [
            f"[0:v]scale={width}:{height},setsar=1[vout]"
        ]

        # Audio mix
        if audio_tracks:
            audio_labels = []
            for i, track in enumerate(audio_tracks, start=1):
                vol = track.get("volume", 1.0)
                label = f"[a{i}]"
                filter_parts.append(
                    f"[{i}:a]volume={vol}{label}"
                )
                audio_labels.append(label)

            mix_input = "".join(audio_labels)
            filter_parts.append(
                f"{mix_input}amix=inputs={len(audio_tracks)}:duration=first:dropout_transition=2[aout]"
            )

            cmd.extend([
                "-filter_complex", ";".join(filter_parts),
                "-map", "[vout]", "-map", "[aout]",
            ])
        else:
            cmd.extend([
                "-filter_complex", ";".join(filter_parts),
                "-map", "[vout]",
            ])

        # Output settings
        cmd.extend([
            "-c:v", "libx264", "-preset", "fast", "-crf", "22",
            "-c:a", "aac", "-b:a", "192k",
            "-r", str(fps),
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
        ])

        if subtitle_file and Path(subtitle_file).exists():
            cmd.extend(["-vf", f"subtitles='{subtitle_file}'"])

        cmd.append(output_path)

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg failed: {result.stderr}")

    return output_path


def probe_duration(video_path: str) -> float:
    """Get video duration in seconds using ffprobe.

    Args:
        video_path: Path to video file.

    Returns:
        Duration in seconds.
    """
    try:
        probe = ffmpeg.probe(video_path)
        duration = float(probe["format"]["duration"])
        return duration
    except Exception:
        return 0.0


def generate_thumbnail(video_path: str, output_path: str, time_offset: float = 0.5) -> str:
    """Extract a thumbnail frame from a video.

    Args:
        video_path: Input video path.
        output_path: Output image path (JPEG).
        time_offset: Timestamp in seconds to extract.

    Returns:
        Output image path.
    """
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(time_offset),
        "-i", video_path,
        "-frames:v", "1",
        "-q:v", "2",
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"Thumbnail extraction failed: {result.stderr}")
    return output_path
