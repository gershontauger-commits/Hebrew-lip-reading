"""Video handling module for recording and managing video files."""

import os
import time
from dataclasses import dataclass
from typing import Optional

import cv2
import numpy as np


@dataclass
class VideoInfo:
    """Information about a video file."""

    path: str
    width: int
    height: int
    fps: float
    frame_count: int
    duration_seconds: float


class VideoHandler:
    """Handles video recording and playback operations."""

    def __init__(self, output_dir: str = "data/videos"):
        """Initialize the video handler.

        Args:
            output_dir: Directory to store recorded videos.
        """
        self.output_dir = output_dir
        self.capture: Optional[cv2.VideoCapture] = None
        self.writer: Optional[cv2.VideoWriter] = None
        self.is_recording = False
        self._ensure_output_dir()

    def _ensure_output_dir(self) -> None:
        """Ensure the output directory exists."""
        os.makedirs(self.output_dir, exist_ok=True)

    def get_available_cameras(self) -> list[int]:
        """Get list of available camera indices.

        Returns:
            List of camera indices that are available.
        """
        available = []
        for i in range(5):  # Check first 5 camera indices
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available.append(i)
                cap.release()
        return available

    def open_camera(self, camera_index: int = 0) -> bool:
        """Open a camera for recording.

        Args:
            camera_index: The camera index to open.

        Returns:
            True if camera was opened successfully.
        """
        if self.capture is not None:
            self.capture.release()

        self.capture = cv2.VideoCapture(camera_index)
        return self.capture.isOpened()

    def close_camera(self) -> None:
        """Close the current camera."""
        if self.capture is not None:
            self.capture.release()
            self.capture = None

    def read_frame(self) -> Optional[np.ndarray]:
        """Read a frame from the camera.

        Returns:
            The frame as a numpy array, or None if reading failed.
        """
        if self.capture is None or not self.capture.isOpened():
            return None

        ret, frame = self.capture.read()
        if ret:
            return frame
        return None

    def start_recording(self, filename: Optional[str] = None, fps: float = 30.0) -> str:
        """Start recording video.

        Args:
            filename: Optional filename. If None, a timestamp-based name is used.
            fps: Frames per second for recording.

        Returns:
            The path to the output video file.
        """
        if self.capture is None or not self.capture.isOpened():
            raise RuntimeError("Camera not opened")

        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"recording_{timestamp}.mp4"

        output_path = os.path.join(self.output_dir, filename)

        width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        self.is_recording = True

        return output_path

    def write_frame(self, frame: np.ndarray) -> None:
        """Write a frame to the recording.

        Args:
            frame: The frame to write.
        """
        if self.writer is not None and self.is_recording:
            self.writer.write(frame)

    def stop_recording(self) -> None:
        """Stop the current recording."""
        if self.writer is not None:
            self.writer.release()
            self.writer = None
        self.is_recording = False

    def get_video_info(self, video_path: str) -> Optional[VideoInfo]:
        """Get information about a video file.

        Args:
            video_path: Path to the video file.

        Returns:
            VideoInfo object, or None if the file could not be read.
        """
        if not os.path.exists(video_path):
            return None

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return None

        try:
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0

            return VideoInfo(
                path=video_path,
                width=width,
                height=height,
                fps=fps,
                frame_count=frame_count,
                duration_seconds=duration,
            )
        finally:
            cap.release()

    def extract_frames(
        self, video_path: str, start_frame: int, end_frame: int
    ) -> list[np.ndarray]:
        """Extract frames from a video file.

        Args:
            video_path: Path to the video file.
            start_frame: Starting frame index (inclusive).
            end_frame: Ending frame index (exclusive).

        Returns:
            List of frames as numpy arrays.
        """
        frames = []
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            return frames

        try:
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
            for _ in range(end_frame - start_frame):
                ret, frame = cap.read()
                if not ret:
                    break
                frames.append(frame)
        finally:
            cap.release()

        return frames

    def save_segment(
        self,
        video_path: str,
        start_frame: int,
        end_frame: int,
        output_filename: str,
    ) -> str:
        """Save a segment of a video to a new file.

        Args:
            video_path: Path to the source video.
            start_frame: Starting frame index.
            end_frame: Ending frame index.
            output_filename: Name of the output file.

        Returns:
            Path to the saved segment.
        """
        info = self.get_video_info(video_path)
        if info is None:
            raise ValueError(f"Could not read video: {video_path}")

        output_path = os.path.join(self.output_dir, output_filename)
        frames = self.extract_frames(video_path, start_frame, end_frame)

        if not frames:
            raise ValueError("No frames extracted")

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(
            output_path, fourcc, info.fps, (info.width, info.height)
        )

        try:
            for frame in frames:
                writer.write(frame)
        finally:
            writer.release()

        return output_path
