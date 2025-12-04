"""
Video Manager Module

Handles video loading, playback, and recording functionality
for the Hebrew Lip Reading application.
"""

import cv2
import numpy as np
from typing import Optional, Tuple


class VideoManager:
    """Manages video operations including loading, playback, and recording."""

    def __init__(self):
        self.video_capture: Optional[cv2.VideoCapture] = None
        self.video_writer: Optional[cv2.VideoWriter] = None
        self.current_frame: Optional[np.ndarray] = None
        self.current_frame_index: int = 0
        self.total_frames: int = 0
        self.fps: float = 30.0
        self.width: int = 0
        self.height: int = 0
        self.is_playing: bool = False
        self.is_recording: bool = False
        self.video_path: Optional[str] = None

    def load_video(self, file_path: str) -> bool:
        """
        Load a video file.

        Args:
            file_path: Path to the video file.

        Returns:
            True if video loaded successfully, False otherwise.
        """
        try:
            self.release()
            self.video_capture = cv2.VideoCapture(file_path)

            if not self.video_capture.isOpened():
                return False

            self.video_path = file_path
            self.total_frames = int(
                self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT)
            )
            self.fps = self.video_capture.get(cv2.CAP_PROP_FPS)
            self.width = int(self.video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.height = int(self.video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.current_frame_index = 0

            # Read first frame
            self.read_current_frame()
            return True

        except Exception as e:
            print(f"Error loading video: {e}")
            return False

    def read_current_frame(self) -> bool:
        """
        Read the current frame from video.

        Returns:
            True if frame read successfully, False otherwise.
        """
        if self.video_capture is None:
            return False

        ret, frame = self.video_capture.read()
        if ret:
            self.current_frame = frame
            return True
        return False

    def get_current_frame(self) -> Optional[np.ndarray]:
        """
        Get the current video frame.

        Returns:
            Current frame as numpy array, or None if no frame available.
        """
        return self.current_frame

    def next_frame(self) -> bool:
        """
        Advance to the next frame.

        Returns:
            True if successful, False if at end of video.
        """
        if self.video_capture is None:
            return False

        if self.current_frame_index < self.total_frames - 1:
            self.current_frame_index += 1
            return self.read_current_frame()
        else:
            self.is_playing = False
            return False

    def prev_frame(self) -> bool:
        """
        Go back to the previous frame.

        Returns:
            True if successful, False if at beginning of video.
        """
        if self.video_capture is None:
            return False

        if self.current_frame_index > 0:
            self.current_frame_index -= 1
            self.video_capture.set(
                cv2.CAP_PROP_POS_FRAMES, self.current_frame_index
            )
            return self.read_current_frame()
        return False

    def seek_frame(self, frame_index: int) -> bool:
        """
        Seek to a specific frame.

        Args:
            frame_index: The frame index to seek to.

        Returns:
            True if successful, False otherwise.
        """
        if self.video_capture is None:
            return False

        if 0 <= frame_index < self.total_frames:
            self.current_frame_index = frame_index
            self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
            return self.read_current_frame()
        return False

    def get_frame_at(self, frame_index: int) -> Optional[np.ndarray]:
        """
        Get a specific frame without changing current position.

        Args:
            frame_index: The frame index to retrieve.

        Returns:
            Frame as numpy array, or None if not available.
        """
        if self.video_capture is None:
            return None

        current_pos = self.current_frame_index
        self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ret, frame = self.video_capture.read()
        self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, current_pos)

        return frame if ret else None

    def get_current_time(self) -> str:
        """
        Get the current playback time as formatted string.

        Returns:
            Time string in HH:MM:SS format.
        """
        if self.fps <= 0:
            return "00:00:00"

        total_seconds = self.current_frame_index / self.fps
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)

        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def frame_to_time(self, frame_index: int) -> float:
        """
        Convert frame index to time in seconds.

        Args:
            frame_index: The frame index.

        Returns:
            Time in seconds.
        """
        if self.fps <= 0:
            return 0.0
        return frame_index / self.fps

    def time_to_frame(self, time_seconds: float) -> int:
        """
        Convert time in seconds to frame index.

        Args:
            time_seconds: Time in seconds.

        Returns:
            Frame index.
        """
        return int(time_seconds * self.fps)

    def start_recording(self, output_path: str) -> bool:
        """
        Start recording from camera.

        Args:
            output_path: Path to save the recorded video.

        Returns:
            True if recording started successfully, False otherwise.
        """
        try:
            # Open camera
            self.video_capture = cv2.VideoCapture(0)

            if not self.video_capture.isOpened():
                return False

            self.width = int(self.video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.height = int(self.video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.fps = 30.0

            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.video_writer = cv2.VideoWriter(
                output_path, fourcc, self.fps, (self.width, self.height)
            )

            if not self.video_writer.isOpened():
                return False

            self.is_recording = True
            self.video_path = output_path
            return True

        except Exception as e:
            print(f"Error starting recording: {e}")
            return False

    def stop_recording(self):
        """Stop recording."""
        self.is_recording = False

        if self.video_writer is not None:
            self.video_writer.release()
            self.video_writer = None

    def capture_recording_frame(self) -> Optional[np.ndarray]:
        """
        Capture and record a frame from camera.

        Returns:
            Captured frame, or None if capture failed.
        """
        if not self.is_recording or self.video_capture is None:
            return None

        ret, frame = self.video_capture.read()
        if ret:
            self.current_frame = frame
            if self.video_writer is not None:
                self.video_writer.write(frame)
            return frame
        return None

    def extract_clip(
        self,
        start_frame: int,
        end_frame: int,
        output_path: str
    ) -> bool:
        """
        Extract a video clip between two frames.

        Args:
            start_frame: Starting frame index.
            end_frame: Ending frame index.
            output_path: Path to save the clip.

        Returns:
            True if clip extracted successfully, False otherwise.
        """
        if self.video_capture is None:
            return False

        try:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(
                output_path, fourcc, self.fps, (self.width, self.height)
            )

            if not writer.isOpened():
                return False

            # Save current position
            current_pos = self.current_frame_index

            # Seek to start frame
            self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

            # Write frames
            for _ in range(end_frame - start_frame + 1):
                ret, frame = self.video_capture.read()
                if ret:
                    writer.write(frame)
                else:
                    break

            writer.release()

            # Restore position
            self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, current_pos)

            return True

        except Exception as e:
            print(f"Error extracting clip: {e}")
            return False

    def release(self):
        """Release video resources."""
        if self.video_capture is not None:
            self.video_capture.release()
            self.video_capture = None

        if self.video_writer is not None:
            self.video_writer.release()
            self.video_writer = None

        self.current_frame = None
        self.is_playing = False
        self.is_recording = False

    def __del__(self):
        """Destructor to ensure resources are released."""
        self.release()
