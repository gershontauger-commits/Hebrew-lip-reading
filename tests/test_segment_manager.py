"""
Tests for the Segment Manager module.
"""

import json
import os
import tempfile
import unittest

from core.segment_manager import Segment, SegmentManager


class TestSegment(unittest.TestCase):
    """Tests for the Segment dataclass."""

    def test_segment_creation(self):
        """Test creating a segment with basic properties."""
        segment = Segment(
            start_frame=0,
            end_frame=100,
            video_path="/path/to/video.mp4",
            fps=30.0
        )

        self.assertEqual(segment.start_frame, 0)
        self.assertEqual(segment.end_frame, 100)
        self.assertEqual(segment.video_path, "/path/to/video.mp4")
        self.assertEqual(segment.fps, 30.0)
        self.assertIsNotNone(segment.id)
        self.assertIsNotNone(segment.created_at)

    def test_segment_duration(self):
        """Test segment duration calculations."""
        segment = Segment(
            start_frame=0,
            end_frame=90,
            video_path="/path/to/video.mp4",
            fps=30.0
        )

        self.assertEqual(segment.duration_frames, 90)
        self.assertEqual(segment.duration_seconds, 3.0)

    def test_segment_time_properties(self):
        """Test segment time property calculations."""
        segment = Segment(
            start_frame=30,
            end_frame=90,
            video_path="/path/to/video.mp4",
            fps=30.0
        )

        self.assertEqual(segment.start_time, 1.0)
        self.assertEqual(segment.end_time, 3.0)

    def test_segment_hebrew_label(self):
        """Test segment with Hebrew label."""
        segment = Segment(
            start_frame=0,
            end_frame=100,
            video_path="/path/to/video.mp4",
            fps=30.0,
            hebrew_label="שלום"
        )

        self.assertEqual(segment.hebrew_label, "שלום")

    def test_segment_to_dict(self):
        """Test converting segment to dictionary."""
        segment = Segment(
            start_frame=0,
            end_frame=100,
            video_path="/path/to/video.mp4",
            fps=30.0,
            hebrew_label="שלום",
            english_label="hello"
        )

        data = segment.to_dict()

        self.assertIsInstance(data, dict)
        self.assertEqual(data["start_frame"], 0)
        self.assertEqual(data["end_frame"], 100)
        self.assertEqual(data["hebrew_label"], "שלום")
        self.assertEqual(data["english_label"], "hello")

    def test_segment_from_dict(self):
        """Test creating segment from dictionary."""
        data = {
            "id": "test-id-123",
            "start_frame": 0,
            "end_frame": 100,
            "video_path": "/path/to/video.mp4",
            "fps": 30.0,
            "hebrew_label": "שלום",
            "english_label": "hello",
            "phonetic_transcription": "",
            "speaker_id": "",
            "notes": "",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00"
        }

        segment = Segment.from_dict(data)

        self.assertEqual(segment.id, "test-id-123")
        self.assertEqual(segment.start_frame, 0)
        self.assertEqual(segment.end_frame, 100)
        self.assertEqual(segment.hebrew_label, "שלום")


class TestSegmentManager(unittest.TestCase):
    """Tests for the SegmentManager class."""

    def setUp(self):
        """Set up test fixtures."""
        # Suppress Qt initialization for testing
        self.manager = SegmentManager()

    def test_add_segment(self):
        """Test adding a segment."""
        segment = Segment(
            start_frame=0,
            end_frame=100,
            video_path="/path/to/video.mp4",
            fps=30.0
        )

        result = self.manager.add_segment(segment)

        self.assertTrue(result)
        self.assertEqual(len(self.manager.segments), 1)

    def test_add_duplicate_segment(self):
        """Test adding a duplicate segment fails."""
        segment = Segment(
            start_frame=0,
            end_frame=100,
            video_path="/path/to/video.mp4",
            fps=30.0
        )

        self.manager.add_segment(segment)
        result = self.manager.add_segment(segment)

        self.assertFalse(result)
        self.assertEqual(len(self.manager.segments), 1)

    def test_get_segment(self):
        """Test getting a segment by ID."""
        segment = Segment(
            start_frame=0,
            end_frame=100,
            video_path="/path/to/video.mp4",
            fps=30.0
        )
        self.manager.add_segment(segment)

        retrieved = self.manager.get_segment(segment.id)

        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.id, segment.id)

    def test_get_nonexistent_segment(self):
        """Test getting a nonexistent segment returns None."""
        retrieved = self.manager.get_segment("nonexistent-id")

        self.assertIsNone(retrieved)

    def test_remove_segment(self):
        """Test removing a segment."""
        segment = Segment(
            start_frame=0,
            end_frame=100,
            video_path="/path/to/video.mp4",
            fps=30.0
        )
        self.manager.add_segment(segment)

        result = self.manager.remove_segment(segment.id)

        self.assertTrue(result)
        self.assertEqual(len(self.manager.segments), 0)

    def test_remove_nonexistent_segment(self):
        """Test removing a nonexistent segment fails."""
        result = self.manager.remove_segment("nonexistent-id")

        self.assertFalse(result)

    def test_update_segment(self):
        """Test updating a segment."""
        segment = Segment(
            start_frame=0,
            end_frame=100,
            video_path="/path/to/video.mp4",
            fps=30.0
        )
        self.manager.add_segment(segment)

        segment.hebrew_label = "שלום"
        result = self.manager.update_segment(segment)

        self.assertTrue(result)
        retrieved = self.manager.get_segment(segment.id)
        self.assertEqual(retrieved.hebrew_label, "שלום")

    def test_get_labeled_segments(self):
        """Test getting labeled segments."""
        segment1 = Segment(
            start_frame=0,
            end_frame=100,
            video_path="/path/to/video.mp4",
            fps=30.0,
            hebrew_label="שלום"
        )
        segment2 = Segment(
            start_frame=100,
            end_frame=200,
            video_path="/path/to/video.mp4",
            fps=30.0
        )
        self.manager.add_segment(segment1)
        self.manager.add_segment(segment2)

        labeled = self.manager.get_labeled_segments()

        self.assertEqual(len(labeled), 1)
        self.assertEqual(labeled[0].hebrew_label, "שלום")

    def test_get_unlabeled_segments(self):
        """Test getting unlabeled segments."""
        segment1 = Segment(
            start_frame=0,
            end_frame=100,
            video_path="/path/to/video.mp4",
            fps=30.0,
            hebrew_label="שלום"
        )
        segment2 = Segment(
            start_frame=100,
            end_frame=200,
            video_path="/path/to/video.mp4",
            fps=30.0
        )
        self.manager.add_segment(segment1)
        self.manager.add_segment(segment2)

        unlabeled = self.manager.get_unlabeled_segments()

        self.assertEqual(len(unlabeled), 1)

    def test_get_segments_by_speaker(self):
        """Test getting segments by speaker."""
        segment1 = Segment(
            start_frame=0,
            end_frame=100,
            video_path="/path/to/video.mp4",
            fps=30.0,
            speaker_id="speaker1"
        )
        segment2 = Segment(
            start_frame=100,
            end_frame=200,
            video_path="/path/to/video.mp4",
            fps=30.0,
            speaker_id="speaker2"
        )
        self.manager.add_segment(segment1)
        self.manager.add_segment(segment2)

        speaker1_segments = self.manager.get_segments_by_speaker("speaker1")

        self.assertEqual(len(speaker1_segments), 1)
        self.assertEqual(speaker1_segments[0].speaker_id, "speaker1")

    def test_save_and_load(self):
        """Test saving and loading segments to/from file."""
        segment = Segment(
            start_frame=0,
            end_frame=100,
            video_path="/path/to/video.mp4",
            fps=30.0,
            hebrew_label="שלום"
        )
        self.manager.add_segment(segment)

        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False
        ) as f:
            temp_path = f.name

        try:
            # Save
            save_result = self.manager.save_to_file(temp_path)
            self.assertTrue(save_result)

            # Load into new manager
            new_manager = SegmentManager()
            load_result = new_manager.load_from_file(temp_path)
            self.assertTrue(load_result)

            # Verify
            self.assertEqual(len(new_manager.segments), 1)
            self.assertEqual(
                new_manager.segments[0].hebrew_label, "שלום"
            )

        finally:
            os.unlink(temp_path)

    def test_clear_segments(self):
        """Test clearing all segments."""
        segment = Segment(
            start_frame=0,
            end_frame=100,
            video_path="/path/to/video.mp4",
            fps=30.0
        )
        self.manager.add_segment(segment)

        self.manager.clear()

        self.assertEqual(len(self.manager.segments), 0)

    def test_get_statistics(self):
        """Test getting segment statistics."""
        segment1 = Segment(
            start_frame=0,
            end_frame=90,
            video_path="/path/to/video.mp4",
            fps=30.0,
            hebrew_label="שלום",
            speaker_id="speaker1"
        )
        segment2 = Segment(
            start_frame=100,
            end_frame=190,
            video_path="/path/to/video.mp4",
            fps=30.0,
            speaker_id="speaker2"
        )
        self.manager.add_segment(segment1)
        self.manager.add_segment(segment2)

        stats = self.manager.get_statistics()

        self.assertEqual(stats["total_segments"], 2)
        self.assertEqual(stats["labeled_segments"], 1)
        self.assertEqual(stats["unlabeled_segments"], 1)
        self.assertEqual(stats["unique_speakers"], 2)
        self.assertEqual(stats["total_duration_seconds"], 6.0)


class TestExportDataset(unittest.TestCase):
    """Tests for dataset export functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = SegmentManager()
        segment = Segment(
            start_frame=0,
            end_frame=100,
            video_path="/path/to/video.mp4",
            fps=30.0,
            hebrew_label="שלום",
            english_label="hello"
        )
        self.manager.add_segment(segment)

    def test_export_csv(self):
        """Test exporting as CSV."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.manager.export_dataset(
                temp_dir, "CSV + Video Clips", None
            )

            self.assertTrue(result)

            csv_path = os.path.join(temp_dir, "segments.csv")
            self.assertTrue(os.path.exists(csv_path))

            with open(csv_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn("שלום", content)
                self.assertIn("hello", content)

    def test_export_json(self):
        """Test exporting as JSON."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.manager.export_dataset(
                temp_dir, "JSON + Video Clips", None
            )

            self.assertTrue(result)

            json_path = os.path.join(temp_dir, "dataset.json")
            self.assertTrue(os.path.exists(json_path))

            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.assertEqual(len(data["segments"]), 1)
                self.assertEqual(
                    data["segments"][0]["hebrew_label"], "שלום"
                )


if __name__ == '__main__':
    unittest.main()
