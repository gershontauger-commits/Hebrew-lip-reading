"""Segment management module for video segments."""

import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional


@dataclass
class Segment:
    """Represents a video segment with Hebrew text label."""

    segment_id: str
    video_path: str
    start_frame: int
    end_frame: int
    hebrew_label: str
    transliteration: str = ""
    speaker_id: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    notes: str = ""

    def duration_frames(self) -> int:
        """Return the number of frames in this segment."""
        return self.end_frame - self.start_frame

    def to_dict(self) -> dict:
        """Convert segment to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Segment":
        """Create a Segment from a dictionary."""
        return cls(**data)


class SegmentManager:
    """Manages a collection of video segments."""

    def __init__(self, data_dir: str = "data/segments"):
        """Initialize the segment manager.

        Args:
            data_dir: Directory to store segment metadata.
        """
        self.data_dir = data_dir
        self.segments: dict[str, Segment] = {}
        self._ensure_data_dir()
        self._load_segments()

    def _ensure_data_dir(self) -> None:
        """Ensure the data directory exists."""
        os.makedirs(self.data_dir, exist_ok=True)

    def _get_metadata_path(self) -> str:
        """Get the path to the metadata file."""
        return os.path.join(self.data_dir, "segments.json")

    def _load_segments(self) -> None:
        """Load segments from the metadata file."""
        metadata_path = self._get_metadata_path()
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, encoding="utf-8") as f:
                    data = json.load(f)
                    for segment_data in data.get("segments", []):
                        segment = Segment.from_dict(segment_data)
                        self.segments[segment.segment_id] = segment
            except (json.JSONDecodeError, KeyError):
                self.segments = {}

    def _save_segments(self) -> None:
        """Save segments to the metadata file."""
        metadata_path = self._get_metadata_path()
        data = {
            "segments": [seg.to_dict() for seg in self.segments.values()],
            "updated_at": datetime.now().isoformat(),
        }
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_segment(self, segment: Segment) -> None:
        """Add a new segment.

        Args:
            segment: The segment to add.
        """
        self.segments[segment.segment_id] = segment
        self._save_segments()

    def remove_segment(self, segment_id: str) -> Optional[Segment]:
        """Remove a segment by ID.

        Args:
            segment_id: The ID of the segment to remove.

        Returns:
            The removed segment, or None if not found.
        """
        segment = self.segments.pop(segment_id, None)
        if segment:
            self._save_segments()
        return segment

    def get_segment(self, segment_id: str) -> Optional[Segment]:
        """Get a segment by ID.

        Args:
            segment_id: The ID of the segment.

        Returns:
            The segment, or None if not found.
        """
        return self.segments.get(segment_id)

    def update_segment(self, segment: Segment) -> None:
        """Update an existing segment.

        Args:
            segment: The segment with updated data.
        """
        if segment.segment_id in self.segments:
            self.segments[segment.segment_id] = segment
            self._save_segments()

    def list_segments(self) -> list[Segment]:
        """Get all segments.

        Returns:
            List of all segments.
        """
        return list(self.segments.values())

    def search_by_label(self, query: str) -> list[Segment]:
        """Search segments by Hebrew label.

        Args:
            query: The search query (Hebrew text).

        Returns:
            List of matching segments.
        """
        return [
            seg
            for seg in self.segments.values()
            if query in seg.hebrew_label or query in seg.transliteration
        ]

    def export_for_ml(self, output_path: str) -> None:
        """Export segments in a format suitable for ML training.

        Args:
            output_path: Path to the output JSON file.
        """
        export_data = []
        for segment in self.segments.values():
            export_data.append(
                {
                    "video_path": segment.video_path,
                    "start_frame": segment.start_frame,
                    "end_frame": segment.end_frame,
                    "label": segment.hebrew_label,
                    "transliteration": segment.transliteration,
                    "speaker_id": segment.speaker_id,
                }
            )
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
