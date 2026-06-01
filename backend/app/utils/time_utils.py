"""Time utility functions for duration calculations."""


def calculate_total_duration(durations: list[float]) -> float:
    """Calculate total duration from a list of shot durations.

    Args:
        durations: List of shot durations in seconds.

    Returns:
        Total duration in seconds.
    """
    return sum(durations)


def seconds_to_timestamp(seconds: float) -> str:
    """Convert seconds to HH:MM:SS.mmm format.

    Args:
        seconds: Time in seconds.

    Returns:
        Formatted timestamp string.
    """
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}"


def seconds_to_srt_time(seconds: float) -> str:
    """Convert seconds to SRT timestamp format (HH:MM:SS,mmm).

    Args:
        seconds: Time in seconds.

    Returns:
        SRT formatted timestamp.
    """
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def generate_srt(
    shots: list[dict],
    start_offset: float = 0.0,
) -> str:
    """Generate SRT subtitle content from shot dialogue.

    Args:
        shots: List of shot dicts with 'dialogue', 'duration', 'order'.
        start_offset: Starting offset in seconds.

    Returns:
        SRT formatted subtitle string.
    """
    lines = []
    cursor = start_offset

    for idx, shot in enumerate(shots):
        dialogue = shot.get("dialogue", "")
        if not dialogue:
            cursor += shot.get("duration", 0)
            continue

        start = seconds_to_srt_time(cursor)
        end = seconds_to_srt_time(cursor + shot.get("duration", 5))
        lines.append(f"{idx + 1}")
        lines.append(f"{start} --> {end}")
        lines.append(dialogue)
        lines.append("")
        cursor += shot.get("duration", 5)

    return "\n".join(lines)
