"""
Segment Manager Module

Handles video segment creation, management, and labeling
for the Hebrew Lip Reading application.
"""

import json
import os
import csv
import uuid
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from PyQt5.QtCore import QObject, pyqtSignal


@dataclass
class Segment:
    """Represents a video segment with labeling information."""

    start_frame: int
    end_frame: int
    video_path: str
    fps: float = 30.0
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    hebrew_label: str = ""
    english_label: str = ""
    phonetic_transcription: str = ""
    speaker_id: str = ""
    notes: str = ""
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self):
        """Initialize timestamps if not set."""
        from datetime import datetime
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()

    @property
    def duration_frames(self) -> int:
        """Get duration in frames."""
        return self.end_frame - self.start_frame

    @property
    def duration_seconds(self) -> float:
        """Get duration in seconds."""
        return self.duration_frames / self.fps if self.fps > 0 else 0.0

    @property
    def start_time(self) -> float:
        """Get start time in seconds."""
        return self.start_frame / self.fps if self.fps > 0 else 0.0

    @property
    def end_time(self) -> float:
        """Get end time in seconds."""
        return self.end_frame / self.fps if self.fps > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert segment to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Segment":
        """Create segment from dictionary."""
        return cls(**data)

    def update_timestamp(self):
        """Update the updated_at timestamp."""
        from datetime import datetime
        self.updated_at = datetime.now().isoformat()


class SegmentManager(QObject):
    """Manages a collection of video segments."""

    # Signals for UI updates
    segment_added = pyqtSignal(object)
    segment_removed = pyqtSignal(str)
    segment_updated = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.segments: List[Segment] = []
        self._segment_map: Dict[str, Segment] = {}

    def add_segment(self, segment: Segment) -> bool:
        """
        Add a new segment.

        Args:
            segment: The segment to add.

        Returns:
            True if segment added successfully, False if ID already exists.
        """
        if segment.id in self._segment_map:
            return False

        self.segments.append(segment)
        self._segment_map[segment.id] = segment
        self.segment_added.emit(segment)
        return True

    def remove_segment(self, segment_id: str) -> bool:
        """
        Remove a segment by ID.

        Args:
            segment_id: The ID of the segment to remove.

        Returns:
            True if segment removed successfully, False if not found.
        """
        if segment_id not in self._segment_map:
            return False

        segment = self._segment_map[segment_id]
        self.segments.remove(segment)
        del self._segment_map[segment_id]
        self.segment_removed.emit(segment_id)
        return True

    def get_segment(self, segment_id: str) -> Optional[Segment]:
        """
        Get a segment by ID.

        Args:
            segment_id: The ID of the segment.

        Returns:
            The segment, or None if not found.
        """
        return self._segment_map.get(segment_id)

    def update_segment(self, segment: Segment) -> bool:
        """
        Update an existing segment.

        Args:
            segment: The segment with updated data.

        Returns:
            True if segment updated successfully, False if not found.
        """
        if segment.id not in self._segment_map:
            return False

        segment.update_timestamp()
        self._segment_map[segment.id] = segment

        # Update in list
        for i, s in enumerate(self.segments):
            if s.id == segment.id:
                self.segments[i] = segment
                break

        self.segment_updated.emit(segment)
        return True

    def get_segments_for_video(self, video_path: str) -> List[Segment]:
        """
        Get all segments for a specific video.

        Args:
            video_path: The video file path.

        Returns:
            List of segments for the video.
        """
        return [s for s in self.segments if s.video_path == video_path]

    def get_labeled_segments(self) -> List[Segment]:
        """
        Get all segments that have labels.

        Returns:
            List of labeled segments.
        """
        return [s for s in self.segments if s.hebrew_label or s.english_label]

    def get_unlabeled_segments(self) -> List[Segment]:
        """
        Get all segments without labels.

        Returns:
            List of unlabeled segments.
        """
        return [
            s for s in self.segments
            if not s.hebrew_label and not s.english_label
        ]

    def get_segments_by_speaker(self, speaker_id: str) -> List[Segment]:
        """
        Get all segments for a specific speaker.

        Args:
            speaker_id: The speaker ID.

        Returns:
            List of segments for the speaker.
        """
        return [s for s in self.segments if s.speaker_id == speaker_id]

    def clear(self):
        """Clear all segments."""
        self.segments.clear()
        self._segment_map.clear()

    def save_to_file(self, file_path: str) -> bool:
        """
        Save segments to a JSON file.

        Args:
            file_path: Path to save the file.

        Returns:
            True if saved successfully, False otherwise.
        """
        try:
            data = {
                "version": "1.0",
                "segments": [s.to_dict() for s in self.segments]
            }
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving segments: {e}")
            return False

    def load_from_file(self, file_path: str) -> bool:
        """
        Load segments from a JSON file.

        Args:
            file_path: Path to the file.

        Returns:
            True if loaded successfully, False otherwise.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.clear()

            for segment_data in data.get("segments", []):
                segment = Segment.from_dict(segment_data)
                self.add_segment(segment)

            return True
        except Exception as e:
            print(f"Error loading segments: {e}")
            return False

    def export_dataset(
        self,
        output_dir: str,
        format_type: str,
        video_manager=None
    ) -> bool:
        """
        Export segments as a machine learning dataset.

        Args:
            output_dir: Directory to export the dataset.
            format_type: Export format (CSV, JSON, TFRecord, WebDataset).
            video_manager: Video manager for extracting clips.

        Returns:
            True if exported successfully, False otherwise.
        """
        try:
            os.makedirs(output_dir, exist_ok=True)

            # Export metadata
            if "CSV" in format_type:
                return self._export_csv(output_dir, video_manager)
            elif "JSON" in format_type:
                return self._export_json(output_dir, video_manager)
            elif "TFRecord" in format_type:
                return self._export_tfrecord(output_dir, video_manager)
            elif "WebDataset" in format_type:
                return self._export_webdataset(output_dir, video_manager)
            else:
                return self._export_csv(output_dir, video_manager)

        except Exception as e:
            print(f"Error exporting dataset: {e}")
            return False

    def _export_csv(self, output_dir: str, video_manager=None) -> bool:
        """Export segments as CSV with video clips."""
        clips_dir = os.path.join(output_dir, "clips")
        os.makedirs(clips_dir, exist_ok=True)

        csv_path = os.path.join(output_dir, "segments.csv")
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                "id", "video_path", "clip_path",
                "start_frame", "end_frame", "start_time", "end_time",
                "duration", "fps",
                "hebrew_label", "english_label",
                "phonetic_transcription", "speaker_id", "notes"
            ])

            for segment in self.segments:
                clip_filename = f"{segment.id[:8]}.mp4"
                clip_path = os.path.join(clips_dir, clip_filename)

                # Extract video clip if video manager provided
                if video_manager and segment.video_path:
                    video_manager.load_video(segment.video_path)
                    video_manager.extract_clip(
                        segment.start_frame,
                        segment.end_frame,
                        clip_path
                    )

                writer.writerow([
                    segment.id,
                    segment.video_path,
                    clip_path if video_manager else "",
                    segment.start_frame,
                    segment.end_frame,
                    segment.start_time,
                    segment.end_time,
                    segment.duration_seconds,
                    segment.fps,
                    segment.hebrew_label,
                    segment.english_label,
                    segment.phonetic_transcription,
                    segment.speaker_id,
                    segment.notes
                ])

        return True

    def _export_json(self, output_dir: str, video_manager=None) -> bool:
        """Export segments as JSON with video clips."""
        clips_dir = os.path.join(output_dir, "clips")
        os.makedirs(clips_dir, exist_ok=True)

        dataset = {
            "version": "1.0",
            "format": "hebrew-lip-reading",
            "segments": []
        }

        for segment in self.segments:
            clip_filename = f"{segment.id[:8]}.mp4"
            clip_path = os.path.join(clips_dir, clip_filename)

            # Extract video clip if video manager provided
            if video_manager and segment.video_path:
                video_manager.load_video(segment.video_path)
                video_manager.extract_clip(
                    segment.start_frame,
                    segment.end_frame,
                    clip_path
                )

            segment_data = segment.to_dict()
            segment_data["clip_path"] = clip_path if video_manager else ""
            dataset["segments"].append(segment_data)

        json_path = os.path.join(output_dir, "dataset.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2)

        return True

    def _export_tfrecord(self, output_dir: str, video_manager=None) -> bool:
        """Export segments as TFRecord format (placeholder)."""
        # TFRecord export would require tensorflow
        # For now, export as JSON with TFRecord-ready structure
        return self._export_json(output_dir, video_manager)

    def _export_webdataset(self, output_dir: str, video_manager=None) -> bool:
        """Export segments as WebDataset format (placeholder)."""
        # WebDataset export would require webdataset package
        # For now, export as JSON with WebDataset-ready structure
        return self._export_json(output_dir, video_manager)

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the segments.

        Returns:
            Dictionary with statistics.
        """
        total_duration = sum(s.duration_seconds for s in self.segments)
        speakers = set(s.speaker_id for s in self.segments if s.speaker_id)

        return {
            "total_segments": len(self.segments),
            "labeled_segments": len(self.get_labeled_segments()),
            "unlabeled_segments": len(self.get_unlabeled_segments()),
            "total_duration_seconds": total_duration,
            "unique_speakers": len(speakers),
            "speakers": list(speakers)
        }
