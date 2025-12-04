"""
Tests for the Video Manager module.
"""

import unittest
from core.video_manager import VideoManager


class TestVideoManager(unittest.TestCase):
    """Tests for the VideoManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = VideoManager()

    def tearDown(self):
        """Clean up after tests."""
        self.manager.release()

    def test_initial_state(self):
        """Test initial state of video manager."""
        self.assertIsNone(self.manager.video_capture)
        self.assertIsNone(self.manager.current_frame)
        self.assertEqual(self.manager.current_frame_index, 0)
        self.assertEqual(self.manager.total_frames, 0)
        self.assertFalse(self.manager.is_playing)
        self.assertFalse(self.manager.is_recording)

    def test_load_nonexistent_video(self):
        """Test loading a nonexistent video file."""
        result = self.manager.load_video("/nonexistent/video.mp4")
        self.assertFalse(result)

    def test_get_current_time_no_video(self):
        """Test getting current time with no video loaded."""
        time = self.manager.get_current_time()
        self.assertEqual(time, "00:00:00")

    def test_frame_to_time(self):
        """Test converting frame to time."""
        self.manager.fps = 30.0
        time = self.manager.frame_to_time(90)
        self.assertEqual(time, 3.0)

    def test_time_to_frame(self):
        """Test converting time to frame."""
        self.manager.fps = 30.0
        frame = self.manager.time_to_frame(3.0)
        self.assertEqual(frame, 90)

    def test_frame_to_time_zero_fps(self):
        """Test frame to time with zero fps."""
        self.manager.fps = 0.0
        time = self.manager.frame_to_time(90)
        self.assertEqual(time, 0.0)

    def test_next_frame_no_video(self):
        """Test next frame with no video loaded."""
        result = self.manager.next_frame()
        self.assertFalse(result)

    def test_prev_frame_no_video(self):
        """Test prev frame with no video loaded."""
        result = self.manager.prev_frame()
        self.assertFalse(result)

    def test_seek_frame_no_video(self):
        """Test seek frame with no video loaded."""
        result = self.manager.seek_frame(0)
        self.assertFalse(result)

    def test_get_frame_at_no_video(self):
        """Test get frame at with no video loaded."""
        frame = self.manager.get_frame_at(0)
        self.assertIsNone(frame)

    def test_release(self):
        """Test releasing video resources."""
        self.manager.release()
        self.assertIsNone(self.manager.video_capture)
        self.assertIsNone(self.manager.current_frame)
        self.assertFalse(self.manager.is_playing)
        self.assertFalse(self.manager.is_recording)


if __name__ == '__main__':
    unittest.main()
