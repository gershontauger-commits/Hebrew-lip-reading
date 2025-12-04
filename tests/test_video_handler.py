"""Tests for the video handler module."""

import os
import tempfile

import numpy as np
import pytest

from hebrew_lip_reading.video_handler import VideoHandler, VideoInfo


class TestVideoHandler:
    """Tests for the VideoHandler class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.handler = VideoHandler(output_dir=self.temp_dir)

    def teardown_method(self):
        """Clean up after tests."""
        self.handler.close_camera()
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_output_directory_created(self):
        """Test that output directory is created."""
        assert os.path.exists(self.temp_dir)

    def test_get_available_cameras(self):
        """Test getting available cameras (may be empty in CI)."""
        cameras = self.handler.get_available_cameras()
        assert isinstance(cameras, list)

    def test_get_video_info_nonexistent(self):
        """Test getting info for nonexistent video."""
        info = self.handler.get_video_info("/nonexistent/video.mp4")
        assert info is None

    def test_extract_frames_nonexistent(self):
        """Test extracting frames from nonexistent video."""
        frames = self.handler.extract_frames("/nonexistent/video.mp4", 0, 10)
        assert frames == []


class TestVideoInfo:
    """Tests for the VideoInfo dataclass."""

    def test_create_video_info(self):
        """Test creating a VideoInfo object."""
        info = VideoInfo(
            path="/path/to/video.mp4",
            width=1920,
            height=1080,
            fps=30.0,
            frame_count=300,
            duration_seconds=10.0,
        )
        assert info.width == 1920
        assert info.height == 1080
        assert info.fps == 30.0
        assert info.duration_seconds == 10.0
