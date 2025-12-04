"""GUI components for the Hebrew Lip Reading application.

This module provides a user-friendly interface with RTL Hebrew text support.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Callable, Optional
import uuid

from PIL import Image, ImageTk

from .segment import Segment, SegmentManager
from .video_handler import VideoHandler


class RTLText(tk.Text):
    """A Text widget with right-to-left support for Hebrew."""

    def __init__(self, master, **kwargs):
        """Initialize the RTL text widget."""
        super().__init__(master, **kwargs)
        # Configure for RTL text
        self.tag_configure("rtl", justify="right")
        self.configure(wrap="word")

    def set_text(self, text: str) -> None:
        """Set the text content with RTL formatting."""
        self.delete("1.0", tk.END)
        self.insert("1.0", text)
        self.tag_add("rtl", "1.0", tk.END)

    def get_text(self) -> str:
        """Get the text content."""
        return self.get("1.0", tk.END).strip()


class RTLEntry(tk.Entry):
    """An Entry widget with right-to-left support for Hebrew."""

    def __init__(self, master, **kwargs):
        """Initialize the RTL entry widget."""
        super().__init__(master, **kwargs)
        # Configure for RTL text
        self.configure(justify="right")


class SegmentListView(ttk.Frame):
    """A widget for displaying and selecting segments."""

    def __init__(
        self,
        master,
        on_select: Optional[Callable[[Segment], None]] = None,
        **kwargs,
    ):
        """Initialize the segment list view.

        Args:
            master: Parent widget.
            on_select: Callback when a segment is selected.
        """
        super().__init__(master, **kwargs)
        self.on_select = on_select
        self.segments: list[Segment] = []

        self._create_widgets()

    def _create_widgets(self) -> None:
        """Create the widget components."""
        # Create treeview
        columns = ("label", "transliteration", "frames", "speaker")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")

        # Configure columns
        self.tree.heading("label", text="תווית (Label)")
        self.tree.heading("transliteration", text="Transliteration")
        self.tree.heading("frames", text="Frames")
        self.tree.heading("speaker", text="Speaker")

        self.tree.column("label", width=150)
        self.tree.column("transliteration", width=150)
        self.tree.column("frames", width=100)
        self.tree.column("speaker", width=100)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Layout
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

    def _on_tree_select(self, event) -> None:
        """Handle tree selection event."""
        if self.on_select is None:
            return

        selection = self.tree.selection()
        if selection:
            item_id = selection[0]
            index = self.tree.index(item_id)
            if 0 <= index < len(self.segments):
                self.on_select(self.segments[index])

    def update_segments(self, segments: list[Segment]) -> None:
        """Update the displayed segments.

        Args:
            segments: List of segments to display.
        """
        self.segments = segments

        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add new items
        for segment in segments:
            frames = f"{segment.start_frame}-{segment.end_frame}"
            self.tree.insert(
                "",
                "end",
                values=(
                    segment.hebrew_label,
                    segment.transliteration,
                    frames,
                    segment.speaker_id,
                ),
            )


class SegmentEditor(ttk.Frame):
    """A widget for editing segment details."""

    def __init__(
        self,
        master,
        on_save: Optional[Callable[[Segment], None]] = None,
        **kwargs,
    ):
        """Initialize the segment editor.

        Args:
            master: Parent widget.
            on_save: Callback when segment is saved.
        """
        super().__init__(master, **kwargs)
        self.on_save = on_save
        self.current_segment: Optional[Segment] = None

        self._create_widgets()

    def _create_widgets(self) -> None:
        """Create the widget components."""
        # Hebrew label
        ttk.Label(self, text="תווית עברית (Hebrew Label):").pack(anchor="e", pady=(10, 0))
        self.hebrew_entry = RTLEntry(self, width=40)
        self.hebrew_entry.pack(fill="x", pady=5)

        # Transliteration
        ttk.Label(self, text="Transliteration:").pack(anchor="e", pady=(10, 0))
        self.trans_entry = ttk.Entry(self, width=40)
        self.trans_entry.pack(fill="x", pady=5)

        # Speaker ID
        ttk.Label(self, text="Speaker ID:").pack(anchor="e", pady=(10, 0))
        self.speaker_entry = ttk.Entry(self, width=40)
        self.speaker_entry.pack(fill="x", pady=5)

        # Frame range
        frame_range = ttk.Frame(self)
        frame_range.pack(fill="x", pady=5)

        ttk.Label(frame_range, text="Start Frame:").pack(side="left")
        self.start_frame_entry = ttk.Entry(frame_range, width=10)
        self.start_frame_entry.pack(side="left", padx=5)

        ttk.Label(frame_range, text="End Frame:").pack(side="left")
        self.end_frame_entry = ttk.Entry(frame_range, width=10)
        self.end_frame_entry.pack(side="left", padx=5)

        # Notes
        ttk.Label(self, text="Notes:").pack(anchor="e", pady=(10, 0))
        self.notes_text = RTLText(self, height=3, width=40)
        self.notes_text.pack(fill="x", pady=5)

        # Save button
        self.save_button = ttk.Button(self, text="שמור (Save)", command=self._on_save)
        self.save_button.pack(pady=10)

    def load_segment(self, segment: Segment) -> None:
        """Load a segment for editing.

        Args:
            segment: The segment to edit.
        """
        self.current_segment = segment

        # Clear and fill fields
        self.hebrew_entry.delete(0, tk.END)
        self.hebrew_entry.insert(0, segment.hebrew_label)

        self.trans_entry.delete(0, tk.END)
        self.trans_entry.insert(0, segment.transliteration)

        self.speaker_entry.delete(0, tk.END)
        self.speaker_entry.insert(0, segment.speaker_id)

        self.start_frame_entry.delete(0, tk.END)
        self.start_frame_entry.insert(0, str(segment.start_frame))

        self.end_frame_entry.delete(0, tk.END)
        self.end_frame_entry.insert(0, str(segment.end_frame))

        self.notes_text.set_text(segment.notes)

    def clear(self) -> None:
        """Clear all fields."""
        self.current_segment = None
        self.hebrew_entry.delete(0, tk.END)
        self.trans_entry.delete(0, tk.END)
        self.speaker_entry.delete(0, tk.END)
        self.start_frame_entry.delete(0, tk.END)
        self.end_frame_entry.delete(0, tk.END)
        self.notes_text.delete("1.0", tk.END)

    def _on_save(self) -> None:
        """Handle save button click."""
        if self.current_segment is None:
            return

        try:
            start_frame = int(self.start_frame_entry.get())
            end_frame = int(self.end_frame_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid frame numbers")
            return

        # Update segment
        self.current_segment.hebrew_label = self.hebrew_entry.get()
        self.current_segment.transliteration = self.trans_entry.get()
        self.current_segment.speaker_id = self.speaker_entry.get()
        self.current_segment.start_frame = start_frame
        self.current_segment.end_frame = end_frame
        self.current_segment.notes = self.notes_text.get_text()

        if self.on_save:
            self.on_save(self.current_segment)


class MainWindow:
    """Main application window."""

    def __init__(self, data_dir: str = "data"):
        """Initialize the main window.

        Args:
            data_dir: Directory for storing data.
        """
        self.data_dir = data_dir
        self.segment_manager = SegmentManager(f"{data_dir}/segments")
        self.video_handler = VideoHandler(f"{data_dir}/videos")

        self.root = tk.Tk()
        self.root.title("Hebrew Lip Reading - קריאת שפתיים בעברית")
        self.root.geometry("1000x700")

        self._create_menu()
        self._create_widgets()
        self._refresh_segments()

    def _create_menu(self) -> None:
        """Create the application menu."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Import Video...", command=self._import_video)
        file_menu.add_command(label="Export for ML...", command=self._export_ml)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Segment menu
        segment_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Segment", menu=segment_menu)
        segment_menu.add_command(label="New Segment...", command=self._new_segment)
        segment_menu.add_command(label="Delete Segment", command=self._delete_segment)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)

    def _create_widgets(self) -> None:
        """Create the main window widgets."""
        # Main container
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill="both", expand=True)

        # Left panel - segment list
        left_panel = ttk.LabelFrame(main_frame, text="Segments - קטעים", padding=10)
        left_panel.pack(side="left", fill="both", expand=True)

        self.segment_list = SegmentListView(left_panel, on_select=self._on_segment_select)
        self.segment_list.pack(fill="both", expand=True)

        # Search
        search_frame = ttk.Frame(left_panel)
        search_frame.pack(fill="x", pady=(10, 0))

        ttk.Label(search_frame, text="חיפוש (Search):").pack(side="left")
        self.search_entry = RTLEntry(search_frame, width=20)
        self.search_entry.pack(side="left", padx=5, fill="x", expand=True)
        ttk.Button(search_frame, text="Search", command=self._search_segments).pack(
            side="left"
        )

        # Right panel - editor
        right_panel = ttk.LabelFrame(main_frame, text="Editor - עורך", padding=10)
        right_panel.pack(side="right", fill="both")

        self.segment_editor = SegmentEditor(right_panel, on_save=self._on_segment_save)
        self.segment_editor.pack(fill="both", expand=True)

        # Status bar
        self.status_var = tk.StringVar(value="Ready - מוכן")
        status_bar = ttk.Label(
            self.root, textvariable=self.status_var, relief="sunken", padding=5
        )
        status_bar.pack(side="bottom", fill="x")

    def _refresh_segments(self) -> None:
        """Refresh the segment list."""
        segments = self.segment_manager.list_segments()
        self.segment_list.update_segments(segments)
        self.status_var.set(f"Loaded {len(segments)} segments - נטענו {len(segments)} קטעים")

    def _on_segment_select(self, segment: Segment) -> None:
        """Handle segment selection."""
        self.segment_editor.load_segment(segment)

    def _on_segment_save(self, segment: Segment) -> None:
        """Handle segment save."""
        self.segment_manager.update_segment(segment)
        self._refresh_segments()
        messagebox.showinfo("Success", "Segment saved successfully - הקטע נשמר בהצלחה")

    def _import_video(self) -> None:
        """Import a video file."""
        file_path = filedialog.askopenfilename(
            title="Select Video - בחר סרטון",
            filetypes=[
                ("Video files", "*.mp4 *.avi *.mov *.mkv"),
                ("All files", "*.*"),
            ],
        )
        if file_path:
            info = self.video_handler.get_video_info(file_path)
            if info:
                self.status_var.set(
                    f"Imported: {file_path} ({info.duration_seconds:.1f}s)"
                )
            else:
                messagebox.showerror("Error", "Could not read video file")

    def _export_ml(self) -> None:
        """Export segments for ML training."""
        file_path = filedialog.asksaveasfilename(
            title="Export for ML - ייצוא ללמידת מכונה",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
        )
        if file_path:
            self.segment_manager.export_for_ml(file_path)
            messagebox.showinfo("Success", f"Exported to {file_path}")

    def _new_segment(self) -> None:
        """Create a new segment."""
        # Create a new segment dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("New Segment - קטע חדש")
        dialog.geometry("400x300")

        # Video path
        ttk.Label(dialog, text="Video Path:").pack(anchor="w", pady=5)
        video_entry = ttk.Entry(dialog, width=40)
        video_entry.pack(fill="x", padx=10)

        def browse_video():
            path = filedialog.askopenfilename(
                filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv")]
            )
            if path:
                video_entry.delete(0, tk.END)
                video_entry.insert(0, path)

        ttk.Button(dialog, text="Browse...", command=browse_video).pack(anchor="e", padx=10)

        # Hebrew label
        ttk.Label(dialog, text="Hebrew Label - תווית עברית:").pack(anchor="e", pady=5)
        label_entry = RTLEntry(dialog, width=40)
        label_entry.pack(fill="x", padx=10)

        # Frame range
        frame_frame = ttk.Frame(dialog)
        frame_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(frame_frame, text="Start:").pack(side="left")
        start_entry = ttk.Entry(frame_frame, width=8)
        start_entry.pack(side="left", padx=5)
        start_entry.insert(0, "0")

        ttk.Label(frame_frame, text="End:").pack(side="left")
        end_entry = ttk.Entry(frame_frame, width=8)
        end_entry.pack(side="left", padx=5)
        end_entry.insert(0, "100")

        def create_segment():
            try:
                segment = Segment(
                    segment_id=str(uuid.uuid4()),
                    video_path=video_entry.get(),
                    start_frame=int(start_entry.get()),
                    end_frame=int(end_entry.get()),
                    hebrew_label=label_entry.get(),
                )
                self.segment_manager.add_segment(segment)
                self._refresh_segments()
                dialog.destroy()
            except ValueError as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(dialog, text="Create - צור", command=create_segment).pack(pady=20)

    def _delete_segment(self) -> None:
        """Delete the selected segment."""
        if self.segment_editor.current_segment is None:
            messagebox.showwarning("Warning", "No segment selected")
            return

        result = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this segment?\nהאם אתה בטוח שברצונך למחוק קטע זה?",
        )
        if result:
            self.segment_manager.remove_segment(
                self.segment_editor.current_segment.segment_id
            )
            self.segment_editor.clear()
            self._refresh_segments()

    def _search_segments(self) -> None:
        """Search segments by label."""
        query = self.search_entry.get()
        if query:
            segments = self.segment_manager.search_by_label(query)
        else:
            segments = self.segment_manager.list_segments()
        self.segment_list.update_segments(segments)
        self.status_var.set(f"Found {len(segments)} segments - נמצאו {len(segments)} קטעים")

    def _show_about(self) -> None:
        """Show the about dialog."""
        messagebox.showinfo(
            "About - אודות",
            "Hebrew Lip Reading Application\n"
            "קריאת שפתיים בעברית\n\n"
            "Version 0.1.0\n\n"
            "A tool for recording, managing, and labeling\n"
            "video segments for Hebrew lip reading research.",
        )

    def run(self) -> None:
        """Run the application."""
        self.root.mainloop()
