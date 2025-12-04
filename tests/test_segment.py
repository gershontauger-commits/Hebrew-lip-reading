"""Tests for the segment management module."""

import json
import os
import tempfile
from datetime import datetime

import pytest

from hebrew_lip_reading.segment import Segment, SegmentManager


class TestSegment:
    """Tests for the Segment class."""

    def test_create_segment(self):
        """Test creating a segment."""
        segment = Segment(
            segment_id="test-1",
            video_path="/path/to/video.mp4",
            start_frame=0,
            end_frame=100,
            hebrew_label="שלום",
            transliteration="shalom",
            speaker_id="speaker-1",
        )
        assert segment.segment_id == "test-1"
        assert segment.hebrew_label == "שלום"
        assert segment.transliteration == "shalom"

    def test_segment_duration(self):
        """Test calculating segment duration in frames."""
        segment = Segment(
            segment_id="test-1",
            video_path="/path/to/video.mp4",
            start_frame=50,
            end_frame=150,
            hebrew_label="מילה",
        )
        assert segment.duration_frames() == 100

    def test_segment_to_dict(self):
        """Test converting segment to dictionary."""
        segment = Segment(
            segment_id="test-1",
            video_path="/path/to/video.mp4",
            start_frame=0,
            end_frame=100,
            hebrew_label="שלום",
        )
        data = segment.to_dict()
        assert data["segment_id"] == "test-1"
        assert data["hebrew_label"] == "שלום"
        assert "created_at" in data

    def test_segment_from_dict(self):
        """Test creating segment from dictionary."""
        data = {
            "segment_id": "test-1",
            "video_path": "/path/to/video.mp4",
            "start_frame": 0,
            "end_frame": 100,
            "hebrew_label": "שלום",
            "transliteration": "shalom",
            "speaker_id": "speaker-1",
            "created_at": "2024-01-01T00:00:00",
            "notes": "",
        }
        segment = Segment.from_dict(data)
        assert segment.segment_id == "test-1"
        assert segment.hebrew_label == "שלום"


class TestSegmentManager:
    """Tests for the SegmentManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = SegmentManager(data_dir=self.temp_dir)

    def teardown_method(self):
        """Clean up after tests."""
        # Clean up temp directory
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_add_segment(self):
        """Test adding a segment."""
        segment = Segment(
            segment_id="test-1",
            video_path="/path/to/video.mp4",
            start_frame=0,
            end_frame=100,
            hebrew_label="שלום",
        )
        self.manager.add_segment(segment)
        assert len(self.manager.list_segments()) == 1

    def test_get_segment(self):
        """Test getting a segment by ID."""
        segment = Segment(
            segment_id="test-1",
            video_path="/path/to/video.mp4",
            start_frame=0,
            end_frame=100,
            hebrew_label="שלום",
        )
        self.manager.add_segment(segment)
        retrieved = self.manager.get_segment("test-1")
        assert retrieved is not None
        assert retrieved.hebrew_label == "שלום"

    def test_remove_segment(self):
        """Test removing a segment."""
        segment = Segment(
            segment_id="test-1",
            video_path="/path/to/video.mp4",
            start_frame=0,
            end_frame=100,
            hebrew_label="שלום",
        )
        self.manager.add_segment(segment)
        removed = self.manager.remove_segment("test-1")
        assert removed is not None
        assert len(self.manager.list_segments()) == 0

    def test_update_segment(self):
        """Test updating a segment."""
        segment = Segment(
            segment_id="test-1",
            video_path="/path/to/video.mp4",
            start_frame=0,
            end_frame=100,
            hebrew_label="שלום",
        )
        self.manager.add_segment(segment)

        segment.hebrew_label = "להתראות"
        self.manager.update_segment(segment)

        retrieved = self.manager.get_segment("test-1")
        assert retrieved.hebrew_label == "להתראות"

    def test_search_by_label(self):
        """Test searching segments by label."""
        segments = [
            Segment(
                segment_id="test-1",
                video_path="/path/to/video.mp4",
                start_frame=0,
                end_frame=100,
                hebrew_label="שלום",
            ),
            Segment(
                segment_id="test-2",
                video_path="/path/to/video.mp4",
                start_frame=100,
                end_frame=200,
                hebrew_label="להתראות",
            ),
            Segment(
                segment_id="test-3",
                video_path="/path/to/video.mp4",
                start_frame=200,
                end_frame=300,
                hebrew_label="שלום עולם",
            ),
        ]
        for seg in segments:
            self.manager.add_segment(seg)

        results = self.manager.search_by_label("שלום")
        assert len(results) == 2

    def test_persistence(self):
        """Test that segments are persisted to disk."""
        segment = Segment(
            segment_id="test-1",
            video_path="/path/to/video.mp4",
            start_frame=0,
            end_frame=100,
            hebrew_label="שלום",
        )
        self.manager.add_segment(segment)

        # Create a new manager with the same directory
        new_manager = SegmentManager(data_dir=self.temp_dir)
        assert len(new_manager.list_segments()) == 1
        assert new_manager.get_segment("test-1").hebrew_label == "שלום"

    def test_export_for_ml(self):
        """Test exporting segments for ML training."""
        segment = Segment(
            segment_id="test-1",
            video_path="/path/to/video.mp4",
            start_frame=0,
            end_frame=100,
            hebrew_label="שלום",
            transliteration="shalom",
            speaker_id="speaker-1",
        )
        self.manager.add_segment(segment)

        export_path = os.path.join(self.temp_dir, "export.json")
        self.manager.export_for_ml(export_path)

        with open(export_path, encoding="utf-8") as f:
            data = json.load(f)

        assert len(data) == 1
        assert data[0]["label"] == "שלום"
        assert data[0]["transliteration"] == "shalom"
